#!/usr/bin/env python3
"""
Script para analizar los datos scrappeados
"""

import sys
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import Settings
from src.services import StorageService


def main():
    """Función principal"""
    settings = Settings()
    storage = StorageService(settings)
    
    # Cargar datos
    jugadores = storage.cargar_jugadores_existentes()
    
    if not jugadores:
        print("⚠️  No hay datos para analizar")
        print(f"   Ejecuta primero: python scripts/run_scraper.py")
        return 1
    
    # Obtener estadísticas
    stats = storage.obtener_estadisticas()
    
    print("\n" + "=" * 80)
    print("📊 ANÁLISIS DE DATOS - ROSARIO CENTRAL")
    print("=" * 80)
    print(f"\nTotal de jugadores: {stats['total']}")
    print(f"Archivo: {settings.JSON_OUTPUT}")
    
    # Análisis por posición
    print(f"\n📍 ANÁLISIS POR POSICIÓN:")
    print("-" * 80)
    for posicion, count in stats['por_posicion'].items():
        porcentaje = (count / stats['total']) * 100
        print(f"{posicion:<30}: {count:>4} jugadores ({porcentaje:>5.1f}%)")
    
    # Análisis por nacionalidad
    print(f"\n🌍 ANÁLISIS POR NACIONALIDAD:")
    print("-" * 80)
    for nacionalidad, count in stats['por_nacionalidad'].items():
        porcentaje = (count / stats['total']) * 100
        print(f"{nacionalidad:<30}: {count:>4} jugadores ({porcentaje:>5.1f}%)")
    
    # Jugadores con más partidos
    print(f"\n🏆 TOP 20 JUGADORES CON MÁS PARTIDOS:")
    print("-" * 80)
    top_20 = sorted(jugadores, key=lambda j: j.partidos, reverse=True)[:20]
    for i, jugador in enumerate(top_20, 1):
        print(f"{i:>2}. {jugador.nombre:<30} - {jugador.partidos:>4} partidos - {jugador.posicion}")
    
    # Estadísticas de partidos
    partidos_list = [j.partidos for j in jugadores]
    print(f"\n📈 ESTADÍSTICAS DE PARTIDOS:")
    print("-" * 80)
    print(f"Promedio: {sum(partidos_list) / len(partidos_list):.1f} partidos")
    print(f"Máximo: {max(partidos_list)} partidos")
    print(f"Mínimo: {min(partidos_list)} partidos")
    print(f"Total acumulado: {sum(partidos_list):,} partidos")
    
    print("\n" + "=" * 80)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
