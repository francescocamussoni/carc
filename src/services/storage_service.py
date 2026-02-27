"""
Servicio para almacenamiento de datos (JSON y CSV)
"""

import json
import csv
import threading
from typing import List, Optional, Set
from datetime import datetime
from pathlib import Path
from ..config import Settings
from ..models import Jugador


class StorageService:
    """
    Servicio para guardar y cargar datos de jugadores
    Maneja persistencia en JSON y CSV
    """
    
    def __init__(self, settings: Optional[Settings] = None):
        """
        Inicializa el servicio de almacenamiento
        
        Args:
            settings: Instancia de Settings (opcional)
        """
        self.settings = settings or Settings()
        self.jugadores: List[Jugador] = []
        self.jugadores_existentes: Set[str] = set()
        
        # Lock para operaciones thread-safe
        self._lock = threading.Lock()
        self._pending_save = []  # Buffer para batch saving
    
    def cargar_jugadores_existentes(self) -> List[Jugador]:
        """
        Carga los jugadores ya guardados desde el JSON
        
        Returns:
            Lista de jugadores cargados
        """
        try:
            if not self.settings.JSON_OUTPUT.exists():
                print(f"📝 Archivo {self.settings.JSON_OUTPUT} no existe, se creará uno nuevo")
                return []
            
            with open(self.settings.JSON_OUTPUT, 'r', encoding='utf-8') as f:
                datos = json.load(f)
                if 'jugadores' in datos:
                    self.jugadores = [Jugador.from_dict(j) for j in datos['jugadores']]
                    self.jugadores_existentes = {j.nombre for j in self.jugadores}
                    print(f"📂 Cargados {len(self.jugadores)} jugadores existentes del archivo")
                    print(f"   Se saltearán estos jugadores en el scraping")
                    return self.jugadores
            
            return []
        
        except Exception as e:
            print(f"⚠️  Error cargando archivo existente: {e}")
            return []
    
    def jugador_existe(self, nombre: str) -> bool:
        """
        Verifica si un jugador ya fue guardado
        
        Args:
            nombre: Nombre del jugador
        
        Returns:
            True si existe, False si no
        """
        return nombre in self.jugadores_existentes
    
    def agregar_jugador(self, jugador: Jugador, batch_mode: bool = False) -> bool:
        """
        Agrega un jugador (thread-safe) y opcionalmente lo guarda
        
        Args:
            jugador: Instancia de Jugador
            batch_mode: Si True, acumula en buffer sin guardar inmediatamente
        
        Returns:
            True si se agregó exitosamente, False si no
        """
        try:
            with self._lock:
                # Agregar a la lista
                self.jugadores.append(jugador)
                self.jugadores_existentes.add(jugador.nombre)
                
                if batch_mode:
                    # Modo batch: acumular en buffer
                    self._pending_save.append(jugador)
                    
                    # Guardar automáticamente cada BATCH_SAVE_SIZE jugadores
                    if len(self._pending_save) >= self.settings.BATCH_SAVE_SIZE:
                        self._flush_batch()
                else:
                    # Modo normal: guardar inmediatamente
                    self.guardar_json()
            
            return True
        
        except Exception as e:
            print(f"      ⚠️  Error guardando jugador: {e}")
            return False
    
    def _flush_batch(self):
        """Guarda el batch acumulado (debe llamarse dentro de un lock)"""
        if self._pending_save:
            self.guardar_json()
            self._pending_save.clear()
    
    def flush_pending(self):
        """Guarda cualquier jugador pendiente en el buffer (thread-safe)"""
        with self._lock:
            self._flush_batch()
    
    def guardar_json(self) -> bool:
        """
        Guarda todos los jugadores en formato JSON (thread-safe)
        
        Returns:
            True si se guardó exitosamente, False si no
        """
        if not self.jugadores:
            return False
        
        try:
            data = {
                'fecha_scraping': datetime.now().isoformat(),
                'total_jugadores': len(self.jugadores),
                'filtro_minimo_partidos': self.settings.MIN_PARTIDOS,
                'jugadores': [j.to_dict() for j in self.jugadores]
            }
            
            # Guardar de forma atómica
            temp_file = str(self.settings.JSON_OUTPUT) + '.tmp'
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            # Renombrar (operación atómica en la mayoría de los sistemas)
            import os
            os.replace(temp_file, self.settings.JSON_OUTPUT)
            
            return True
        
        except Exception as e:
            print(f"❌ Error guardando JSON: {e}")
            return False
    
    def guardar_csv(self) -> bool:
        """
        Guarda todos los jugadores en formato CSV
        
        Returns:
            True si se guardó exitosamente, False si no
        """
        if not self.jugadores:
            return False
        
        try:
            with open(self.settings.CSV_OUTPUT, 'w', newline='', encoding='utf-8') as f:
                # Incluir clubes_historia y url_perfil en el CSV
                writer = csv.DictWriter(
                    f, 
                    fieldnames=['nombre', 'nacionalidad', 'posicion', 'partidos', 'image_profile', 'clubes_historia', 'url_perfil', 'fuente']
                )
                writer.writeheader()
                
                # Convertir clubes_historia a string JSON para CSV
                import json as json_lib
                rows = []
                for j in self.jugadores:
                    row = j.to_dict()
                    if row.get('clubes_historia'):
                        row['clubes_historia'] = json_lib.dumps(row['clubes_historia'], ensure_ascii=False)
                    rows.append(row)
                
                writer.writerows(rows)
            
            return True
        
        except Exception as e:
            print(f"❌ Error guardando CSV: {e}")
            return False
    
    def obtener_estadisticas(self) -> dict:
        """
        Genera estadísticas de los jugadores guardados
        
        Returns:
            Diccionario con estadísticas
        """
        if not self.jugadores:
            return {}
        
        # Top jugadores por partidos
        top_jugadores = sorted(self.jugadores, key=lambda j: j.partidos, reverse=True)[:10]
        
        # Distribución por posición
        posiciones = {}
        for j in self.jugadores:
            posiciones[j.posicion] = posiciones.get(j.posicion, 0) + 1
        
        # Distribución por nacionalidad
        nacionalidades = {}
        for j in self.jugadores:
            nacionalidades[j.nacionalidad] = nacionalidades.get(j.nacionalidad, 0) + 1
        
        # Estadísticas de clubes
        jugadores_con_clubes = sum(1 for j in self.jugadores if j.clubes_historia and len(j.clubes_historia) > 0)
        total_clubes = sum(len(j.clubes_historia) for j in self.jugadores if j.clubes_historia)
        
        # Estadísticas de tarjetas
        jugadores_con_tarjetas = sum(1 for j in self.jugadores if j.tarjetas_por_torneo and len(j.tarjetas_por_torneo) > 0)
        total_amarillas = 0
        total_doble_amarillas = 0
        total_rojas = 0
        
        for j in self.jugadores:
            if j.tarjetas_por_torneo:
                for torneo in j.tarjetas_por_torneo:
                    total_amarillas += torneo.get('amarillas', 0)
                    total_doble_amarillas += torneo.get('doble_amarillas', 0)
                    total_rojas += torneo.get('rojas', 0)
        
        # Estadísticas de goles y minutos
        jugadores_con_goles = sum(1 for j in self.jugadores if j.goles_por_torneo and len(j.goles_por_torneo) > 0)
        total_goles = 0
        total_minutos = 0
        jugadores_con_minutos = 0
        
        for j in self.jugadores:
            if j.goles_por_torneo:
                jugador_tiene_minutos = False
                for torneo in j.goles_por_torneo:
                    total_goles += torneo.get('goles', 0)
                    minutos_torneo = torneo.get('minutos', 0)
                    total_minutos += minutos_torneo
                    if minutos_torneo > 0:
                        jugador_tiene_minutos = True
                if jugador_tiene_minutos:
                    jugadores_con_minutos += 1
        
        return {
            'total': len(self.jugadores),
            'top_10': top_jugadores,
            'por_posicion': dict(sorted(posiciones.items(), key=lambda x: x[1], reverse=True)),
            'por_nacionalidad': dict(sorted(nacionalidades.items(), key=lambda x: x[1], reverse=True)),
            'con_historia_clubes': jugadores_con_clubes,
            'total_clubes_registrados': total_clubes,
            'con_tarjetas': jugadores_con_tarjetas,
            'total_amarillas': total_amarillas,
            'total_doble_amarillas': total_doble_amarillas,
            'total_rojas': total_rojas,
            'con_goles': jugadores_con_goles,
            'total_goles': total_goles,
            'con_minutos': jugadores_con_minutos,
            'total_minutos': total_minutos
        }
