"""
Scraper para obtener goles detallados de jugadores de Rosario Central
"""

import json
import time
import random
import threading
from typing import Dict, Optional
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

from ..config import Settings
from ..utils import HTTPClient
from ..services import GolesDetalladosService
from ..models import GolesJugador, GolIndividual


class GolesDetalladosScraper:
    """
    Scraper para obtener información detallada de todos los goles
    marcados por jugadores de Rosario Central
    
    Estructura del JSON resultante:
    {
        "fecha_scraping": "...",
        "total_jugadores": N,
        "jugadores": {
            "Marco Ruben": {
                "url_perfil": "...",
                "total_goles": 106,
                "goles": [...]
            }
        }
    }
    """
    
    def __init__(self, settings: Optional[Settings] = None):
        """
        Inicializa el scraper
        
        Args:
            settings: Instancia de Settings (opcional)
        """
        self.settings = settings or Settings()
        self.http_client = HTTPClient(self.settings)
        self.goles_service = GolesDetalladosService(self.settings, self.http_client)
        
        # Archivo de salida
        self.output_file = self.settings.GOLES_DETALLADOS_OUTPUT
        
        # Diccionario de jugadores y sus goles {nombre: GolesJugador}
        self.jugadores_dict: Dict[str, GolesJugador] = {}
        
        # Lock para operaciones thread-safe
        self._lock = threading.Lock()
    
    def cargar_jugadores_principales(self) -> list:
        """
        Carga jugadores desde rosario_central_jugadores.json
        
        Returns:
            Lista de diccionarios con datos de jugadores
        """
        jugadores_file = self.settings.JSON_OUTPUT
        
        if not jugadores_file.exists():
            print(f"⚠️  No se encontró {jugadores_file}")
            print("   Ejecuta primero: python scripts/run_scraper.py")
            return []
        
        try:
            with open(jugadores_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                jugadores = data.get('jugadores', [])
                print(f"✅ Cargados {len(jugadores)} jugadores desde {jugadores_file.name}")
                return jugadores
        except Exception as e:
            print(f"❌ Error cargando jugadores: {e}")
            return []
    
    def cargar_goles_existentes(self):
        """Carga goles ya scrapeados para evitar duplicados"""
        if self.output_file.exists():
            try:
                with open(self.output_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    jugadores_data = data.get('jugadores', {})
                    
                    # Reconstruir diccionario de jugadores
                    for nombre, jugador_data in jugadores_data.items():
                        self.jugadores_dict[nombre] = GolesJugador.from_dict(nombre, jugador_data)
                    
                    if self.jugadores_dict:
                        total_goles = sum(j.total_goles for j in self.jugadores_dict.values())
                        print(f"✅ Cargados {len(self.jugadores_dict)} jugadores con {total_goles} goles")
            except Exception as e:
                print(f"⚠️  Error cargando goles existentes: {e}")
    
    def guardar_goles(self):
        """Guarda los goles en formato JSON agrupados por jugador"""
        try:
            with self._lock:
                # Crear directorio si no existe
                self.output_file.parent.mkdir(parents=True, exist_ok=True)
                
                # Calcular totales
                total_jugadores = len(self.jugadores_dict)
                total_goles = sum(j.total_goles for j in self.jugadores_dict.values())
                
                # Construir diccionario de salida
                jugadores_dict = {}
                for nombre, jugador in self.jugadores_dict.items():
                    jugadores_dict[nombre] = jugador.to_dict()
                
                data = {
                    'fecha_scraping': datetime.now().isoformat(),
                    'total_jugadores': total_jugadores,
                    'total_goles': total_goles,
                    'descripcion': 'Goles marcados por jugadores de Rosario Central con información detallada',
                    'jugadores': jugadores_dict
                }
                
                # Guardar con operación atómica (temp file + rename)
                temp_file = str(self.output_file) + '.tmp'
                with open(temp_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                
                import os
                os.replace(temp_file, self.output_file)
                
                return True
        except Exception as e:
            print(f"❌ Error guardando goles: {e}")
            return False
    
    def _procesar_jugador(self, jugador: dict) -> Optional[GolesJugador]:
        """
        Procesa un jugador individual (worker para ThreadPoolExecutor)
        
        Args:
            jugador: Diccionario con datos del jugador
        
        Returns:
            GolesJugador si tiene goles, None si no
        """
        nombre = jugador.get('nombre', '')
        url_perfil = jugador.get('url_perfil', '')
        
        if not url_perfil:
            print(f"      ⚠️  {nombre}: Sin URL de perfil")
            return None
        
        try:
            # Obtener goles
            goles = self.goles_service.obtener_goles_jugador(url_perfil, nombre)
            
            if goles:
                jugador_goles = GolesJugador(
                    nombre=nombre,
                    url_perfil=url_perfil,
                    total_goles=len(goles),
                    goles=goles
                )
                return jugador_goles
            else:
                print(f"      ℹ️  {nombre}: Sin goles")
                return None
        
        except Exception as e:
            print(f"      ❌ {nombre}: Error - {e}")
            return None
    
    def scrape(self, max_jugadores: Optional[int] = None, paralelo: bool = True) -> Dict[str, GolesJugador]:
        """
        Ejecuta el scraping de goles detallados
        
        Args:
            max_jugadores: Límite de jugadores a procesar (None = todos)
            paralelo: Si True, usa ThreadPoolExecutor para paralelización
        
        Returns:
            Diccionario con jugadores y sus goles
        """
        print()
        print("=" * 80)
        print("🎯 SCRAPER DE GOLES DETALLADOS - ROSARIO CENTRAL")
        print("=" * 80)
        print()
        
        # Cargar jugadores principales
        jugadores = self.cargar_jugadores_principales()
        if not jugadores:
            return {}
        
        # Cargar goles existentes
        self.cargar_goles_existentes()
        
        # Filtrar jugadores ya procesados
        jugadores_pendientes = [
            j for j in jugadores 
            if j.get('nombre') not in self.jugadores_dict
        ]
        
        if max_jugadores:
            jugadores_pendientes = jugadores_pendientes[:max_jugadores]
        
        print(f"📊 Jugadores pendientes: {len(jugadores_pendientes)}")
        print(f"✅ Jugadores ya procesados: {len(self.jugadores_dict)}")
        print()
        
        if not jugadores_pendientes:
            print("✨ Todos los jugadores ya fueron procesados")
            return self.jugadores_dict
        
        # Procesar jugadores
        procesados = 0
        errores = 0
        
        if paralelo and len(jugadores_pendientes) > 1:
            print(f"🔄 Procesando {len(jugadores_pendientes)} jugadores en paralelo...")
            print()
            
            with ThreadPoolExecutor(max_workers=self.settings.MAX_WORKERS) as executor:
                # Submit tasks
                futures = {
                    executor.submit(self._procesar_jugador, jug): jug
                    for jug in jugadores_pendientes
                }
                
                # Process results
                for i, future in enumerate(as_completed(futures), 1):
                    jugador = futures[future]
                    nombre = jugador.get('nombre', '?')
                    
                    try:
                        resultado = future.result()
                        
                        if resultado:
                            with self._lock:
                                self.jugadores_dict[resultado.nombre] = resultado
                                procesados += 1
                            
                            # Guardar cada N jugadores
                            if procesados % self.settings.BATCH_SAVE_SIZE == 0:
                                self.guardar_goles()
                                print(f"\n💾 Guardado parcial ({procesados} jugadores)\n")
                        
                        print(f"   [{i}/{len(jugadores_pendientes)}] ✓ {nombre}")
                    
                    except Exception as e:
                        errores += 1
                        print(f"   [{i}/{len(jugadores_pendientes)}] ✗ {nombre}: {e}")
                    
                    # Delay entre requests
                    delay = random.uniform(*self.settings.DELAY_ENTRE_JUGADORES)
                    time.sleep(delay)
        
        else:
            # Modo secuencial
            print(f"🔄 Procesando {len(jugadores_pendientes)} jugadores secuencialmente...")
            print()
            
            for i, jugador in enumerate(jugadores_pendientes, 1):
                nombre = jugador.get('nombre', '?')
                
                try:
                    resultado = self._procesar_jugador(jugador)
                    
                    if resultado:
                        self.jugadores_dict[resultado.nombre] = resultado
                        procesados += 1
                        
                        # Guardar cada N jugadores
                        if procesados % self.settings.BATCH_SAVE_SIZE == 0:
                            self.guardar_goles()
                            print(f"\n💾 Guardado parcial ({procesados} jugadores)\n")
                    
                    print(f"   [{i}/{len(jugadores_pendientes)}] ✓ {nombre}")
                
                except Exception as e:
                    errores += 1
                    print(f"   [{i}/{len(jugadores_pendientes)}] ✗ {nombre}: {e}")
                
                delay = random.uniform(*self.settings.DELAY_ENTRE_JUGADORES)
                time.sleep(delay)
        
        # Guardar resultado final
        print()
        print("💾 Guardando resultado final...")
        self.guardar_goles()
        
        # Mostrar estadísticas
        self._mostrar_estadisticas()
        
        return self.jugadores_dict
    
    def _mostrar_estadisticas(self):
        """Muestra estadísticas de los goles scrapeados"""
        print()
        print("=" * 80)
        print("📊 ESTADÍSTICAS DE GOLES DETALLADOS")
        print("=" * 80)
        
        if not self.jugadores_dict:
            print("Sin datos")
            return
        
        total_jugadores = len(self.jugadores_dict)
        total_goles = sum(j.total_goles for j in self.jugadores_dict.values())
        
        print(f"\nTotal de jugadores con goles: {total_jugadores}")
        print(f"Total de goles documentados: {total_goles}")
        
        # Top 10 goleadores
        top_goleadores = sorted(
            self.jugadores_dict.items(),
            key=lambda x: x[1].total_goles,
            reverse=True
        )[:10]
        
        print(f"\n🏆 TOP 10 GOLEADORES:")
        print("-" * 80)
        for i, (nombre, jugador) in enumerate(top_goleadores, 1):
            print(f"{i:>2}. {nombre:<40} {jugador.total_goles:>3} goles")
        
        # Estadísticas de goles con información completa
        goles_con_minuto = sum(
            1 for j in self.jugadores_dict.values() 
            for g in j.goles if g.minuto
        )
        goles_con_tipo = sum(
            1 for j in self.jugadores_dict.values() 
            for g in j.goles if g.tipo_gol
        )
        
        print(f"\n📋 CALIDAD DE DATOS:")
        print("-" * 80)
        print(f"Goles con minuto: {goles_con_minuto}/{total_goles} ({goles_con_minuto/total_goles*100:.1f}%)")
        print(f"Goles con tipo: {goles_con_tipo}/{total_goles} ({goles_con_tipo/total_goles*100:.1f}%)")
        
        print()
        print("=" * 80)
