#!/usr/bin/env python3
"""
Script principal para ejecutar el scraper de Rosario Central
"""

import sys
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import Settings
from src.scrapers import TransfermarktScraper
from src.services import StorageService


def print_banner():
    """Imprime el banner de inicio"""
    print("=" * 80)
    print("⚽ SCRAPER DE JUGADORES HISTÓRICOS DE ROSARIO CENTRAL")
    print("=" * 80)
    print()


def print_info(settings: Settings):
    """Imprime información de configuración"""
    print("ℹ️  Scraping completo de Transfermarkt:")
    print("   ✅ Partidos de TODOS los torneos (liga + copas + internacionales)")
    print("   ✅ Posiciones específicas (Lateral izquierdo, Extremo derecho, etc.)")
    print("   ✅ Fotos de perfil en alta calidad")
    print("   ✅ Historia completa de clubes (carrera profesional)")
    print("   ✅ Estadísticas por torneo: goles, minutos, amarillas, rojas")
    print("   ⏱️  Nota: Obtiene TODA la información en un solo proceso")
    print(f"   📊 Filtro mínimo: {settings.MIN_PARTIDOS} partidos")
    print()


def print_estadisticas(storage: StorageService):
    """Imprime estadísticas finales"""
    stats = storage.obtener_estadisticas()
    
    if not stats:
        print("\n⚠️  No hay datos para mostrar")
        return
    
    print("\n" + "=" * 80)
    print("📊 ESTADÍSTICAS DE ROSARIO CENTRAL")
    print("=" * 80)
    print(f"Total de jugadores (>{storage.settings.MIN_PARTIDOS} partidos): {stats['total']}")
    
    # Top 10
    print(f"\n🏆 TOP 10 JUGADORES CON MÁS PARTIDOS:")
    print("-" * 80)
    print(f"{'#':<4}{'Nombre':<35}{'Nacionalidad':<20}{'Pos':<10}{'PJ':<8}")
    print("-" * 80)
    for i, jugador in enumerate(stats['top_10'], 1):
        print(f"{i:<4}{jugador.nombre:<35}{jugador.nacionalidad:<20}{jugador.posicion:<10}{jugador.partidos:<8}")
    
    # Distribución por posición
    print(f"\n📍 DISTRIBUCIÓN POR POSICIÓN:")
    print("-" * 80)
    for posicion, count in list(stats['por_posicion'].items())[:10]:
        print(f"{posicion:<30}: {count:>4} jugadores")
    
    # Distribución por nacionalidad
    print(f"\n🌍 TOP 5 NACIONALIDADES:")
    print("-" * 80)
    for nacionalidad, count in list(stats['por_nacionalidad'].items())[:5]:
        print(f"{nacionalidad:<30}: {count:>4} jugadores")
    
    # Estadísticas de clubes
    if 'con_historia_clubes' in stats:
        print(f"\n🏟️  HISTORIA DE CLUBES:")
        print("-" * 80)
        print(f"Jugadores con historia completa: {stats['con_historia_clubes']}/{stats['total']}")
        if stats['total_clubes_registrados'] > 0:
            promedio = stats['total_clubes_registrados'] / stats['con_historia_clubes'] if stats['con_historia_clubes'] > 0 else 0
            print(f"Total de clubes registrados   : {stats['total_clubes_registrados']}")
            print(f"Promedio de clubes por jugador: {promedio:.1f}")
    
    # Estadísticas de tarjetas
    if 'con_tarjetas' in stats:
        print(f"\n🟨 TARJETAS EN ROSARIO CENTRAL:")
        print("-" * 80)
        print(f"Jugadores con tarjetas registradas: {stats['con_tarjetas']}/{stats['total']}")
        if stats['total_amarillas'] > 0 or stats['total_rojas'] > 0:
            print(f"Total de amarillas              : {stats['total_amarillas']}")
            print(f"Total de doble amarillas        : {stats['total_doble_amarillas']}")
            print(f"Total de rojas                  : {stats['total_rojas']}")
    
    # Estadísticas de goles
    if 'con_goles' in stats:
        print(f"\n⚽ GOLES EN ROSARIO CENTRAL:")
        print("-" * 80)
        print(f"Jugadores con goles registrados : {stats['con_goles']}/{stats['total']}")
        if stats['total_goles'] > 0:
            print(f"Total de goles                  : {stats['total_goles']}")
            promedio = stats['total_goles'] / stats['con_goles'] if stats['con_goles'] > 0 else 0
            print(f"Promedio de goles por goleador  : {promedio:.1f}")
    
    # Estadísticas de minutos
    if 'con_minutos' in stats and stats['total_minutos'] > 0:
        print(f"\n⏱️  MINUTOS JUGADOS EN ROSARIO CENTRAL:")
        print("-" * 80)
        print(f"Jugadores con minutos registrados: {stats['con_minutos']}/{stats['total']}")
        print(f"Total de minutos jugados         : {stats['total_minutos']:,}'")
        
        # Convertir a horas y partidos equivalentes
        horas = stats['total_minutos'] / 60
        partidos_equivalentes = stats['total_minutos'] / 90
        print(f"Equivalente en horas             : {horas:,.1f} horas")
        print(f"Equivalente en partidos (90 min) : {partidos_equivalentes:,.1f} partidos")
        
        if stats['con_minutos'] > 0:
            promedio = stats['total_minutos'] / stats['con_minutos']
            print(f"Promedio de minutos por jugador  : {promedio:,.0f}'")
    
    print("=" * 80)
    print()


def main():
    """Función principal"""
    try:
        # Banner
        print_banner()
        
        # Configuración
        settings = Settings()
        
        # Puedes personalizar la configuración aquí
        # settings.update(MIN_PARTIDOS=5, MAX_PAGINAS=20)
        
        # Info
        print_info(settings)
        
        # Crear scraper
        scraper = TransfermarktScraper(settings=settings)
        
        # Ejecutar scraping
        jugadores = scraper.run()
        
        # Estadísticas
        print_estadisticas(scraper.storage)
        
        print(f"\n💾 Datos guardados en: {settings.JSON_OUTPUT}")
        print(f"💾 Datos guardados en: {settings.CSV_OUTPUT}")
        print(f"\n✅ ¡Scraping completado exitosamente!")
        
        return 0
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Programa interrumpido por el usuario")
        return 1
    
    except Exception as e:
        print(f"\n❌ Error fatal: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
