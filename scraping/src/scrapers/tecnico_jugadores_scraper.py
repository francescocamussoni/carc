"""
Scraper para obtener jugadores dirigidos por cada técnico en Rosario Central.
"""

import json
import time
import random
import threading
import re
from typing import Dict, Optional, List, Tuple
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

from ..config import Settings
from ..utils import HTTPClient
from ..services import TecnicoJugadoresService
from ..models import JugadoresTecnico, JugadoresPorTorneo, ResumenJugador


class TecnicoJugadoresScraper:
    """
    Scraper para obtener todos los jugadores dirigidos por cada técnico,
    agrupados por torneo y temporada.
    """
    
    def __init__(self, settings: Optional[Settings] = None):
        self.settings = settings or Settings()
        self.http_client = HTTPClient(self.settings)
        self.jugadores_service = TecnicoJugadoresService(self.settings, self.http_client)
        
        self.output_file = self.settings.TECNICOS_JUGADORES_OUTPUT
        self.tecnicos_file = self.settings.TECNICOS_OUTPUT
        
        self.tecnicos_jugadores_dict: Dict[str, JugadoresTecnico] = {}
        self._lock = threading.Lock()
    
    def cargar_jugadores_existentes(self):
        """Carga jugadores ya scrapeados para evitar reprocesarlos."""
        if self.output_file.exists():
            try:
                with open(self.output_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    tecnicos_data = data.get('tecnicos', {})
                    for nombre, tecnico_data in tecnicos_data.items():
                        self.tecnicos_jugadores_dict[nombre] = JugadoresTecnico.from_dict(nombre, tecnico_data)
                    if self.tecnicos_jugadores_dict:
                        print(f"✅ Cargados {len(self.tecnicos_jugadores_dict)} técnicos con jugadores")
            except Exception as e:
                print(f"⚠️  Error cargando jugadores existentes: {e}")
    
    def cargar_tecnicos_base(self) -> Dict[str, dict]:
        """
        Carga la información base de técnicos desde el JSON principal.
        
        Returns:
            Dict con nombre como clave y datos básicos del técnico
        """
        if not self.tecnicos_file.exists():
            print(f"❌ No se encontró el archivo de técnicos: {self.tecnicos_file}")
            return {}
        
        try:
            with open(self.tecnicos_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                tecnicos_data = data.get('tecnicos', {})
                print(f"✅ Cargados {len(tecnicos_data)} técnicos base")
                return tecnicos_data
        except Exception as e:
            print(f"❌ Error cargando técnicos base: {e}")
            return {}
    
    def guardar_jugadores(self):
        """Guarda los jugadores dirigidos en el archivo JSON."""
        try:
            with self._lock:
                self.output_file.parent.mkdir(parents=True, exist_ok=True)
                
                tecnicos_dict = {
                    nombre: tecnico.to_dict() 
                    for nombre, tecnico in self.tecnicos_jugadores_dict.items()
                }
                
                # Calcular estadísticas
                total_torneos = sum(
                    len(t.torneos) 
                    for t in self.tecnicos_jugadores_dict.values()
                )
                total_jugadores_unicos = self._contar_jugadores_unicos()
                
                data = {
                    'fecha_scraping': datetime.now().isoformat(),
                    'total_tecnicos': len(self.tecnicos_jugadores_dict),
                    'total_torneos': total_torneos,
                    'total_jugadores_unicos': total_jugadores_unicos,
                    'descripcion': 'Jugadores dirigidos por cada técnico en Rosario Central, agrupados por torneo',
                    'tecnicos': tecnicos_dict
                }
                
                # Guardar atómicamente
                temp_file = str(self.output_file) + '.tmp'
                with open(temp_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                
                import os
                os.replace(temp_file, self.output_file)
                
                return True
        except Exception as e:
            print(f"❌ Error guardando jugadores: {e}")
            return False
    
    def _contar_jugadores_unicos(self) -> int:
        """Cuenta el total de jugadores únicos en todos los técnicos."""
        jugadores_unicos = set()
        for tecnico in self.tecnicos_jugadores_dict.values():
            for torneo in tecnico.torneos:
                for jugador in torneo.jugadores:
                    jugadores_unicos.add(jugador.nombre)
        return len(jugadores_unicos)
    
    def _extraer_trainer_id(self, url_perfil: str) -> Optional[str]:
        """
        Extrae el ID del técnico de su URL de perfil.
        
        Args:
            url_perfil: URL del perfil del técnico
        
        Returns:
            ID del técnico o None si no se pudo extraer
        """
        # URL format: /nombre-apellido/profil/trainer/ID
        match = re.search(r'/trainer/(\d+)', url_perfil)
        if match:
            return match.group(1)
        return None
    
    def _extraer_nombre_url(self, url_perfil: str) -> Optional[str]:
        """
        Extrae el nombre en formato URL de la URL de perfil.
        
        Args:
            url_perfil: URL del perfil del técnico (ej: '/miguel-angel-russo/profil/trainer/2738')
        
        Returns:
            Nombre en formato URL (ej: 'miguel-angel-russo') o None
        """
        # URL format: /nombre-apellido/profil/trainer/ID
        match = re.search(r'/([^/]+)/profil/trainer/', url_perfil)
        if match:
            return match.group(1)
        return None
    
    def _calcular_resumen_general(self, torneos: List[JugadoresPorTorneo]) -> List[ResumenJugador]:
        """
        Calcula el resumen general de jugadores dirigidos en todas las temporadas.
        
        Args:
            torneos: Lista de torneos con jugadores
        
        Returns:
            Lista de ResumenJugador ordenada por apariciones
        """
        from collections import defaultdict
        
        # Acumular estadísticas por jugador
        jugadores_stats = defaultdict(lambda: {
            'apariciones': 0,
            'goles': 0,
            'asistencias': 0,
            'minutos': 0,
            'temporadas': set()
        })
        
        for torneo in torneos:
            for jugador in torneo.jugadores:
                jugadores_stats[jugador.nombre]['apariciones'] += jugador.apariciones
                jugadores_stats[jugador.nombre]['goles'] += jugador.goles
                jugadores_stats[jugador.nombre]['asistencias'] += jugador.asistencias
                jugadores_stats[jugador.nombre]['minutos'] += jugador.minutos
                jugadores_stats[jugador.nombre]['temporadas'].add(torneo.temporada)
        
        # Convertir a ResumenJugador
        resumen = []
        for nombre, stats in jugadores_stats.items():
            resumen.append(ResumenJugador(
                nombre=nombre,
                total_apariciones=stats['apariciones'],
                total_goles=stats['goles'],
                total_asistencias=stats['asistencias'],
                total_minutos=stats['minutos'],
                temporadas=len(stats['temporadas'])
            ))
        
        # Ordenar por apariciones (mayor a menor)
        resumen.sort(key=lambda x: x.total_apariciones, reverse=True)
        
        # Retornar top 20
        return resumen[:20]
    
    def _procesar_tecnico(self, tecnico_info: Tuple[str, dict]) -> Optional[JugadoresTecnico]:
        """
        Procesa un técnico y extrae todos sus jugadores dirigidos.
        
        Args:
            tecnico_info: Tupla (nombre, datos del técnico)
        
        Returns:
            JugadoresTecnico o None si hay error
        """
        nombre, datos = tecnico_info
        url_perfil = datos.get('url_perfil', '')
        
        if not url_perfil:
            print(f"   ⚠️  {nombre}: Sin URL de perfil")
            return None
        
        trainer_id = self._extraer_trainer_id(url_perfil)
        nombre_url = self._extraer_nombre_url(url_perfil)
        
        if not trainer_id or not nombre_url:
            print(f"   ⚠️  {nombre}: No se pudo extraer ID o nombre URL de {url_perfil}")
            return None
        
        try:
            # Obtener jugadores dirigidos
            torneos = self.jugadores_service.obtener_jugadores_por_tecnico(trainer_id, nombre, nombre_url)
            
            if not torneos:
                print(f"   ⚠️  {nombre}: No se encontraron jugadores")
                return None
            
            # Calcular resumen general
            jugadores_mas_dirigidos = self._calcular_resumen_general(torneos)
            
            tecnico_jugadores = JugadoresTecnico(
                nombre_tecnico=nombre,
                url_perfil=url_perfil,
                torneos=torneos,
                jugadores_mas_dirigidos=jugadores_mas_dirigidos
            )
            
            return tecnico_jugadores
        
        except Exception as e:
            print(f"   ❌ {nombre}: Error - {e}")
            return None
    
    def scrape(self, max_tecnicos: Optional[int] = None, paralelo: bool = True) -> Dict[str, JugadoresTecnico]:
        """
        Ejecuta el scraping de jugadores para todos los técnicos.
        
        Args:
            max_tecnicos: Límite de técnicos a procesar (para testing)
            paralelo: Si True, usa procesamiento paralelo
        
        Returns:
            Dict con los jugadores dirigidos por cada técnico
        """
        print("\n" + "=" * 80 + "\n⚽ SCRAPER DE JUGADORES DIRIGIDOS POR TÉCNICOS\n" + "=" * 80 + "\n")
        
        # Cargar técnicos base
        tecnicos_base = self.cargar_tecnicos_base()
        
        if not tecnicos_base:
            print("❌ No se encontraron técnicos para procesar")
            return {}
        
        # Cargar jugadores ya existentes
        self.cargar_jugadores_existentes()
        
        # Filtrar técnicos pendientes
        tecnicos_pendientes = [
            (nombre, datos) 
            for nombre, datos in tecnicos_base.items()
            if nombre not in self.tecnicos_jugadores_dict
        ]
        
        if max_tecnicos:
            tecnicos_pendientes = tecnicos_pendientes[:max_tecnicos]
        
        print(f"📊 Técnicos pendientes: {len(tecnicos_pendientes)}")
        print(f"✅ Técnicos ya procesados: {len(self.tecnicos_jugadores_dict)}")
        print()
        
        if not tecnicos_pendientes:
            print("✨ Todos los técnicos ya fueron procesados")
            return self.tecnicos_jugadores_dict
        
        procesados = 0
        errores = 0
        
        if paralelo and len(tecnicos_pendientes) > 1:
            print(f"🔄 Procesando {len(tecnicos_pendientes)} técnicos en paralelo...\n")
            
            with ThreadPoolExecutor(max_workers=self.settings.MAX_WORKERS) as executor:
                futures = {
                    executor.submit(self._procesar_tecnico, tec): tec 
                    for tec in tecnicos_pendientes
                }
                
                for i, future in enumerate(as_completed(futures), 1):
                    tecnico_info = futures[future]
                    nombre = tecnico_info[0]
                    
                    try:
                        resultado = future.result()
                        if resultado:
                            with self._lock:
                                self.tecnicos_jugadores_dict[resultado.nombre_tecnico] = resultado
                                procesados += 1
                            
                            # Guardar periódicamente
                            if procesados % self.settings.BATCH_SAVE_SIZE == 0:
                                self.guardar_jugadores()
                                print(f"\n💾 Guardado parcial ({procesados} técnicos)\n")
                        
                        print(f"   [{i}/{len(tecnicos_pendientes)}] ✓ {nombre}")
                    
                    except Exception as e:
                        errores += 1
                        print(f"   [{i}/{len(tecnicos_pendientes)}] ✗ {nombre}: {e}")
                    
                    # Delay entre requests
                    delay = random.uniform(*self.settings.DELAY_ENTRE_JUGADORES)
                    time.sleep(delay)
        
        else:
            print(f"🔄 Procesando {len(tecnicos_pendientes)} técnicos secuencialmente...\n")
            
            for i, tecnico_info in enumerate(tecnicos_pendientes, 1):
                nombre = tecnico_info[0]
                
                try:
                    resultado = self._procesar_tecnico(tecnico_info)
                    if resultado:
                        self.tecnicos_jugadores_dict[resultado.nombre_tecnico] = resultado
                        procesados += 1
                    
                    print(f"   [{i}/{len(tecnicos_pendientes)}] ✓ {nombre}")
                
                except Exception as e:
                    errores += 1
                    print(f"   [{i}/{len(tecnicos_pendientes)}] ✗ {nombre}: {e}")
                
                delay = random.uniform(*self.settings.DELAY_ENTRE_JUGADORES)
                time.sleep(delay)
        
        # Guardar resultado final
        self.guardar_jugadores()
        self._mostrar_estadisticas()
        self._mostrar_ejemplos()
        
        return self.tecnicos_jugadores_dict
    
    def _mostrar_estadisticas(self):
        """Muestra estadísticas del scraping."""
        print("\n" + "=" * 80 + "\n📊 ESTADÍSTICAS GENERALES\n" + "=" * 80 + "\n")
        
        if not self.tecnicos_jugadores_dict:
            print("Sin datos")
            return
        
        total_tecnicos = len(self.tecnicos_jugadores_dict)
        total_torneos = sum(len(t.torneos) for t in self.tecnicos_jugadores_dict.values())
        total_jugadores_unicos = self._contar_jugadores_unicos()
        
        print(f"Total técnicos: {total_tecnicos}")
        print(f"Total torneos: {total_torneos}")
        print(f"Jugadores únicos: {total_jugadores_unicos}")
        
        # Top técnicos por torneos dirigidos
        top_torneos = sorted(
            self.tecnicos_jugadores_dict.items(),
            key=lambda x: len(x[1].torneos),
            reverse=True
        )[:10]
        
        print(f"\n🏆 TOP 10 TÉCNICOS POR TORNEOS DIRIGIDOS:")
        print("-" * 80)
        for i, (nombre, tecnico) in enumerate(top_torneos, 1):
            total_jugadores = sum(len(t.jugadores) for t in tecnico.torneos)
            print(f"{i:>2}. {nombre:<40} {len(tecnico.torneos):>2} torneos ({total_jugadores} jugadores)")
        
        print("\n" + "=" * 80 + "\n")
    
    def _mostrar_ejemplos(self):
        """Muestra ejemplos del formato de salida."""
        print("📊 Ejemplos de formato:\n" + "=" * 80 + "\n")
        
        # Mostrar 3 ejemplos
        ejemplos = ["Miguel Ángel Russo", "Carlos Tevez", "Ariel Holan"]
        
        for nombre_ejemplo in ejemplos:
            tecnico = self.tecnicos_jugadores_dict.get(nombre_ejemplo)
            if tecnico:
                print(f"{tecnico.nombre_tecnico}:")
                print(f"  📊 Total torneos: {len(tecnico.torneos)}")
                
                if tecnico.torneos:
                    # Mostrar primer torneo como ejemplo
                    torneo = tecnico.torneos[0]
                    print(f"  🏆 Ejemplo - {torneo.torneo} ({torneo.temporada}):")
                    print(f"     Jugadores: {torneo.total_jugadores}")
                    
                    # Mostrar top 3 jugadores por apariciones
                    top_jugadores = sorted(
                        torneo.jugadores, 
                        key=lambda x: x.apariciones, 
                        reverse=True
                    )[:3]
                    
                    for j in top_jugadores:
                        print(f"       • {j.nombre} ({j.posicion}): {j.apariciones} partidos, {j.goles} goles")
                
                print()
        
        print("=" * 80 + "\n")
