"""
Scraper principal para obtener información de técnicos de Rosario Central
"""

import json
import time
import random
import threading
from typing import Dict, Optional, Tuple, List
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict

from ..config import Settings
from ..utils import HTTPClient
from ..services import (
    TecnicoService, 
    TecnicoClubesService, 
    TecnicoStatsService,
    TecnicoImageService
)
from ..models import Tecnico, InfoRosario, PeriodoRosario


class TecnicoScraper:
    """
    Scraper para obtener información completa de técnicos de Rosario Central
    
    Estructura del JSON resultante:
    {
        "fecha_scraping": "...",
        "total_tecnicos": N,
        "tecnicos": {
            "Carlos Tevez": {
                "url_perfil": "...",
                "nacionalidad": "...",
                ...
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
        
        # Servicios
        self.tecnico_service = TecnicoService(self.settings, self.http_client)
        self.clubes_service = TecnicoClubesService(self.settings, self.http_client)
        self.stats_service = TecnicoStatsService(self.settings, self.http_client)
        self.image_service = TecnicoImageService(self.settings, self.http_client)
        
        # Archivo de salida
        self.output_file = self.settings.TECNICOS_OUTPUT
        
        # Diccionario de técnicos {nombre: Tecnico}
        self.tecnicos_dict: Dict[str, Tecnico] = {}
        
        # Lock para operaciones thread-safe
        self._lock = threading.Lock()
    
    def cargar_tecnicos_existentes(self):
        """Carga técnicos ya scrapeados para evitar duplicados"""
        if self.output_file.exists():
            try:
                with open(self.output_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    tecnicos_data = data.get('tecnicos', {})
                    
                    # Reconstruir diccionario de técnicos
                    for nombre, tecnico_data in tecnicos_data.items():
                        self.tecnicos_dict[nombre] = Tecnico.from_dict(nombre, tecnico_data)
                    
                    if self.tecnicos_dict:
                        print(f"✅ Cargados {len(self.tecnicos_dict)} técnicos existentes")
            except Exception as e:
                print(f"⚠️  Error cargando técnicos existentes: {e}")
    
    def guardar_tecnicos(self):
        """Guarda los técnicos en formato JSON"""
        try:
            with self._lock:
                # Crear directorio si no existe
                self.output_file.parent.mkdir(parents=True, exist_ok=True)
                
                # Construir diccionario de salida
                tecnicos_dict = {}
                for nombre, tecnico in self.tecnicos_dict.items():
                    tecnicos_dict[nombre] = tecnico.to_dict()
                
                data = {
                    'fecha_scraping': datetime.now().isoformat(),
                    'total_tecnicos': len(self.tecnicos_dict),
                    'descripcion': 'Técnicos que dirigieron Rosario Central con información completa',
                    'tecnicos': tecnicos_dict
                }
                
                # Guardar con operación atómica
                temp_file = str(self.output_file) + '.tmp'
                with open(temp_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                
                import os
                os.replace(temp_file, self.output_file)
                
                return True
        except Exception as e:
            print(f"❌ Error guardando técnicos: {e}")
            return False
    
    def _procesar_tecnico(self, tecnico_data: Tuple[str, str, List[Tuple[str, int]]]) -> Optional[Tecnico]:
        """
        Procesa un técnico individual (worker para ThreadPoolExecutor)
        
        Args:
            tecnico_data: Tupla (nombre, url_perfil, lista_periodos)
                         lista_periodos es List[(periodo, partidos)]
        
        Returns:
            Tecnico con información completa o None
        """
        nombre, url_perfil, periodos_list = tecnico_data
        
        try:
            # Obtener información básica del perfil
            tecnico = self.tecnico_service.obtener_info_completa_tecnico(url_perfil, nombre)
            
            if not tecnico:
                return None
            
            # Construir InfoRosario con todos los periodos
            periodos_rosario = []
            total_partidos = 0
            
            for periodo_str, partidos in periodos_list:
                periodos_rosario.append(PeriodoRosario(
                    periodo=periodo_str,
                    partidos_dirigidos=partidos
                ))
                total_partidos += partidos
            
            tecnico.info_rosario = InfoRosario(
                periodos=periodos_rosario,
                total_periodos=len(periodos_rosario),
                total_partidos=total_partidos
            )
            
            # Descargar imagen
            tecnico.image_profile = self.image_service.descargar_imagen_tecnico(url_perfil, nombre)
            
            # Obtener clubes dirigidos (opcional, puede fallar silenciosamente)
            try:
                tecnico.clubes_historia = self.clubes_service.obtener_clubes_tecnico(url_perfil, nombre)
            except:
                tecnico.clubes_historia = []
            
            # No intentamos obtener estadísticas detalladas porque la URL no existe para la mayoría
            # Los partidos ya los tenemos desde la tabla principal
            tecnico.estadisticas_por_torneo = []
            
            return tecnico
        
        except Exception as e:
            print(f"      ❌ {nombre}: Error - {e}")
            return None
    
    def scrape(self, max_tecnicos: Optional[int] = None, paralelo: bool = True) -> Dict[str, Tecnico]:
        """
        Ejecuta el scraping de técnicos
        
        Args:
            max_tecnicos: Límite de técnicos a procesar (None = todos)
            paralelo: Si True, usa ThreadPoolExecutor para paralelización
        
        Returns:
            Diccionario con técnicos procesados
        """
        print()
        print("=" * 80)
        print("👔 SCRAPER DE TÉCNICOS - ROSARIO CENTRAL")
        print("=" * 80)
        print()
        
        # Obtener lista de técnicos
        tecnicos_info = self.tecnico_service.obtener_tecnicos_rosario_central()
        
        if not tecnicos_info:
            print("❌ No se encontraron técnicos")
            return {}
        
        # AGRUPAR técnicos por nombre (para combinar múltiples periodos)
        tecnicos_agrupados = defaultdict(lambda: {'url': '', 'periodos': []})
        
        for nombre, url, periodo, partidos in tecnicos_info:
            tecnicos_agrupados[nombre]['url'] = url
            tecnicos_agrupados[nombre]['periodos'].append((periodo, partidos))
        
        print(f"📋 Total de registros: {len(tecnicos_info)}")
        print(f"👤 Técnicos únicos: {len(tecnicos_agrupados)}")
        
        # Mostrar técnicos con múltiples pasos
        tecnicos_multiples = {
            nombre: len(data['periodos']) 
            for nombre, data in tecnicos_agrupados.items() 
            if len(data['periodos']) > 1
        }
        if tecnicos_multiples:
            print(f"🔄 Técnicos con múltiples pasos por el club: {len(tecnicos_multiples)}")
            for nombre, cantidad in sorted(tecnicos_multiples.items(), key=lambda x: x[1], reverse=True)[:5]:
                print(f"   • {nombre}: {cantidad} periodos")
        print()
        
        # Cargar técnicos existentes
        self.cargar_tecnicos_existentes()
        
        # Crear lista de técnicos para procesar (agrupados)
        tecnicos_pendientes = [
            (nombre, data['url'], data['periodos'])
            for nombre, data in tecnicos_agrupados.items()
            if nombre not in self.tecnicos_dict
        ]
        
        if max_tecnicos:
            tecnicos_pendientes = tecnicos_pendientes[:max_tecnicos]
        
        print(f"📊 Técnicos pendientes: {len(tecnicos_pendientes)}")
        print(f"✅ Técnicos ya procesados: {len(self.tecnicos_dict)}")
        print()
        
        if not tecnicos_pendientes:
            print("✨ Todos los técnicos ya fueron procesados")
            return self.tecnicos_dict
        
        # Procesar técnicos
        procesados = 0
        errores = 0
        
        if paralelo and len(tecnicos_pendientes) > 1:
            print(f"🔄 Procesando {len(tecnicos_pendientes)} técnicos en paralelo...")
            print()
            
            with ThreadPoolExecutor(max_workers=self.settings.MAX_WORKERS) as executor:
                # Submit tasks
                futures = {
                    executor.submit(self._procesar_tecnico, tec): tec
                    for tec in tecnicos_pendientes
                }
                
                # Process results
                for i, future in enumerate(as_completed(futures), 1):
                    tecnico_info = futures[future]
                    nombre = tecnico_info[0]
                    
                    try:
                        resultado = future.result()
                        
                        if resultado:
                            with self._lock:
                                self.tecnicos_dict[resultado.nombre] = resultado
                                procesados += 1
                            
                            # Guardar cada N técnicos
                            if procesados % self.settings.BATCH_SAVE_SIZE == 0:
                                self.guardar_tecnicos()
                                print(f"\n💾 Guardado parcial ({procesados} técnicos)\n")
                        
                        print(f"   [{i}/{len(tecnicos_pendientes)}] ✓ {nombre}")
                    
                    except Exception as e:
                        errores += 1
                        print(f"   [{i}/{len(tecnicos_pendientes)}] ✗ {nombre}: {e}")
                    
                    # Delay entre requests
                    delay = random.uniform(*self.settings.DELAY_ENTRE_JUGADORES)
                    time.sleep(delay)
        
        else:
            # Modo secuencial
            print(f"🔄 Procesando {len(tecnicos_pendientes)} técnicos secuencialmente...")
            print()
            
            for i, tecnico_info in enumerate(tecnicos_pendientes, 1):
                nombre = tecnico_info[0]
                
                try:
                    resultado = self._procesar_tecnico(tecnico_info)
                    
                    if resultado:
                        self.tecnicos_dict[resultado.nombre] = resultado
                        procesados += 1
                        
                        # Guardar cada N técnicos
                        if procesados % self.settings.BATCH_SAVE_SIZE == 0:
                            self.guardar_tecnicos()
                            print(f"\n💾 Guardado parcial ({procesados} técnicos)\n")
                    
                    print(f"   [{i}/{len(tecnicos_pendientes)}] ✓ {nombre}")
                
                except Exception as e:
                    errores += 1
                    print(f"   [{i}/{len(tecnicos_pendientes)}] ✗ {nombre}: {e}")
                
                delay = random.uniform(*self.settings.DELAY_ENTRE_JUGADORES)
                time.sleep(delay)
        
        # Guardar resultado final
        print()
        print("💾 Guardando resultado final...")
        self.guardar_tecnicos()
        
        # Mostrar estadísticas
        self._mostrar_estadisticas()
        
        return self.tecnicos_dict
    
    def _mostrar_estadisticas(self):
        """Muestra estadísticas de los técnicos scrapeados"""
        print()
        print("=" * 80)
        print("📊 ESTADÍSTICAS DE TÉCNICOS")
        print("=" * 80)
        
        if not self.tecnicos_dict:
            print("Sin datos")
            return
        
        total_tecnicos = len(self.tecnicos_dict)
        total_partidos = sum(t.info_rosario.total_partidos for t in self.tecnicos_dict.values())
        total_periodos = sum(t.info_rosario.total_periodos for t in self.tecnicos_dict.values())
        
        print(f"\nTotal de técnicos: {total_tecnicos}")
        print(f"Total de periodos: {total_periodos}")
        print(f"Total de partidos dirigidos: {total_partidos}")
        
        # Top 10 por partidos dirigidos
        top_tecnicos = sorted(
            self.tecnicos_dict.items(),
            key=lambda x: x[1].info_rosario.total_partidos,
            reverse=True
        )[:10]
        
        print(f"\n🏆 TOP 10 POR PARTIDOS DIRIGIDOS:")
        print("-" * 80)
        for i, (nombre, tecnico) in enumerate(top_tecnicos, 1):
            periodos_info = f" ({tecnico.info_rosario.total_periodos} periodo{'s' if tecnico.info_rosario.total_periodos > 1 else ''})"
            print(f"{i:>2}. {nombre:<40} {tecnico.info_rosario.total_partidos:>3} partidos{periodos_info}")
        
        # Técnicos con info completa
        con_foto = sum(1 for t in self.tecnicos_dict.values() if t.image_profile)
        con_clubes = sum(1 for t in self.tecnicos_dict.values() if t.clubes_historia)
        con_stats = sum(1 for t in self.tecnicos_dict.values() if t.estadisticas_por_torneo)
        
        print(f"\n📋 CALIDAD DE DATOS:")
        print("-" * 80)
        print(f"Con foto: {con_foto}/{total_tecnicos} ({con_foto/total_tecnicos*100:.1f}%)")
        print(f"Con historia de clubes: {con_clubes}/{total_tecnicos} ({con_clubes/total_tecnicos*100:.1f}%)")
        print(f"Con estadísticas: {con_stats}/{total_tecnicos} ({con_stats/total_tecnicos*100:.1f}%)")
        
        print()
        print("=" * 80)
