"""
Script para descargar escudos de todos los clubes scrapeados.

Este script:
1. Extrae todos los clubes únicos de jugadores y técnicos
2. Descarga el escudo de cada club desde Transfermarkt
3. Guarda los escudos en data/images/clubes/
"""

import sys
import json
from pathlib import Path
from typing import Set, Dict, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import Settings
from src.services import ClubImageService


class ClubImagesScraper:
    """
    Scraper para descargar escudos de clubes.
    """
    
    def __init__(self, settings: Settings):
        """
        Inicializa el scraper.
        
        Args:
            settings: Configuración del proyecto
        """
        self.settings = settings
        self.club_service = ClubImageService(settings)
        self.lock = threading.Lock()
        self.clubes_procesados: Dict[str, str] = {}
    
    def extraer_clubes_jugadores(self) -> Set[Tuple[str, str, str]]:
        """
        Extrae todos los clubes únicos del JSON de jugadores.
        
        Returns:
            Set de tuplas (nombre_club, pais, club_url)
        """
        clubes = set()
        
        try:
            with open(self.settings.JSON_OUTPUT, 'r') as f:
                data = json.load(f)
            
            for jugador in data.get('jugadores', []):
                for club in jugador.get('clubes_historia', []):
                    nombre = club.get('nombre', '').strip()
                    pais = club.get('pais', '').strip()
                    club_url = club.get('club_url', '').strip()  # ✅ NUEVO
                    if nombre:
                        clubes.add((nombre, pais, club_url))
            
            print(f'✅ Encontrados {len(clubes)} clubes únicos en jugadores')
            return clubes
        
        except Exception as e:
            print(f'❌ Error extrayendo clubes de jugadores: {e}')
            return set()
    
    def extraer_clubes_tecnicos(self) -> Set[Tuple[str, str, str]]:
        """
        Extrae todos los clubes únicos del JSON de técnicos.
        
        Returns:
            Set de tuplas (nombre_club, pais, club_url)
        """
        clubes = set()
        
        try:
            with open(self.settings.TECNICOS_OUTPUT, 'r') as f:
                data = json.load(f)
            
            for tecnico_data in data.get('tecnicos', {}).values():
                for club in tecnico_data.get('clubes_historia', []):
                    nombre = club.get('nombre', '').strip()
                    pais = club.get('pais', '').strip()
                    club_url = club.get('club_url', '').strip()  # ✅ NUEVO
                    if nombre:
                        clubes.add((nombre, pais, club_url))
            
            print(f'✅ Encontrados {len(clubes)} clubes únicos en técnicos')
            return clubes
        
        except Exception as e:
            print(f'❌ Error extrayendo clubes de técnicos: {e}')
            return set()
    
    def extraer_todos_clubes(self) -> Set[Tuple[str, str, str]]:
        """
        Extrae todos los clubes únicos de jugadores y técnicos.
        
        Returns:
            Set de tuplas (nombre_club, pais, club_url)
        """
        clubes_jugadores = self.extraer_clubes_jugadores()
        clubes_tecnicos = self.extraer_clubes_tecnicos()
        
        todos_clubes = clubes_jugadores.union(clubes_tecnicos)
        
        print(f'\n📊 Total de clubes únicos: {len(todos_clubes)}')
        
        return todos_clubes
    
    def _procesar_club(self, club_info: Tuple[str, str, str]) -> Tuple[str, str, bool]:
        """
        Procesa un club (descarga su escudo).
        
        Args:
            club_info: Tupla (nombre_club, pais, club_url)
        
        Returns:
            Tupla (nombre_club, ruta_imagen, exito)
        """
        nombre_club, pais, club_url = club_info
        
        try:
            print(f'   🔍 Descargando: {nombre_club} ({pais})')
            
            # ✅ NUEVO: Pasar la URL del club al servicio
            ruta_imagen = self.club_service.buscar_y_descargar_escudo(nombre_club, pais, club_url)
            
            if ruta_imagen:
                with self.lock:
                    self.clubes_procesados[nombre_club] = ruta_imagen
                return (nombre_club, ruta_imagen, True)
            else:
                return (nombre_club, '', False)
        
        except Exception as e:
            print(f'   ❌ Error con {nombre_club}: {e}')
            return (nombre_club, '', False)
    
    def descargar_escudos(self, clubes: Set[Tuple[str, str, str]], max_workers: int = 5):
        """
        Descarga escudos de todos los clubes en paralelo.
        
        Args:
            clubes: Set de tuplas (nombre_club, pais, club_url)
            max_workers: Número de workers paralelos
        """
        print(f'\n🔄 Descargando escudos ({max_workers} workers en paralelo)...\n')
        
        exitosos = 0
        fallidos = 0
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Enviar todas las tareas
            future_to_club = {
                executor.submit(self._procesar_club, club_info): club_info 
                for club_info in clubes
            }
            
            # Procesar resultados
            for i, future in enumerate(as_completed(future_to_club), 1):
                nombre_club, ruta_imagen, exito = future.result()
                
                if exito:
                    exitosos += 1
                    print(f'[{i}/{len(clubes)}] ✓ {nombre_club}')
                else:
                    fallidos += 1
                    print(f'[{i}/{len(clubes)}] ✗ {nombre_club}')
        
        # Resumen
        print(f'\n{"="*80}')
        print(f'📊 RESUMEN')
        print(f'{"="*80}')
        print(f'✅ Escudos descargados: {exitosos}')
        print(f'❌ Fallidos: {fallidos}')
        print(f'💾 Ubicación: data/images/clubes/')
        print(f'{"="*80}\n')


def main():
    """Función principal del script."""
    print('\n' + '='*80)
    print('🏆 SCRAPER DE ESCUDOS DE CLUBES')
    print('='*80)
    print('\nEste script descarga los escudos de todos los clubes scrapeados')
    print('desde Transfermarkt y los guarda en data/images/clubes/')
    print()
    
    # Confirmación
    respuesta = input('¿Deseas continuar? (s/n): ').lower().strip()
    if respuesta != 's':
        print('❌ Operación cancelada')
        return
    
    # Inicializar
    settings = Settings()
    scraper = ClubImagesScraper(settings)
    
    # Extraer clubes
    print(f'\n{"="*80}')
    print('📋 EXTRAYENDO CLUBES')
    print('='*80 + '\n')
    
    clubes = scraper.extraer_todos_clubes()
    
    if not clubes:
        print('❌ No se encontraron clubes para procesar')
        return
    
    # Descargar escudos
    scraper.descargar_escudos(clubes, max_workers=5)
    
    print('✅ ¡Proceso completado!')


if __name__ == '__main__':
    main()
