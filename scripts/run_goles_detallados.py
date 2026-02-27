#!/usr/bin/env python3
"""
Script para scrappear goles detallados de jugadores de Rosario Central
"""

import sys
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import Settings
from src.scrapers.goles_detallados_scraper import GolesDetalladosScraper


def print_banner():
    """Imprime el banner de inicio"""
    print()
    print("=" * 80)
    print("⚽ SCRAPER DE GOLES DETALLADOS - ROSARIO CENTRAL")
    print("=" * 80)
    print()
    print("Este scraper obtiene información detallada de todos los goles marcados")
    print("por jugadores de Rosario Central:")
    print()
    print("  ✅ Rival contra el que marcó")
    print("  ✅ Competición y temporada")
    print("  ✅ Minuto del gol")
    print("  ✅ Tipo de gol (cabeza, tiro izquierda, penalti, etc.)")
    print("  ✅ Marcador al momento del gol")
    print("  ✅ Marcador final del partido")
    print("  ✅ Local/Visitante")
    print()
    print("📋 Requisito: Debe existir rosario_central_jugadores.json")
    print("   (Ejecutar primero: python scripts/run_scraper.py)")
    print()


def print_info():
    """Imprime información adicional"""
    print("ℹ️  Configuración:")
    print("   • Lee jugadores de: data/output/rosario_central_jugadores.json")
    print("   • Guarda goles en: data/output/rosario_central_goles_detallados.json")
    print("   • Scraping incremental: Saltea jugadores ya procesados")
    print("   • Procesamiento paralelo: 4 workers simultáneos")
    print()
    print("⏱️  Tiempo estimado:")
    print("   • ~3-5 segundos por jugador")
    print("   • 100 jugadores: ~7-10 minutos")
    print()


def main():
    """Función principal"""
    try:
        # Banner
        print_banner()
        print_info()
        
        # Preguntar confirmación
        respuesta = input("¿Deseas continuar? (s/n): ").strip().lower()
        if respuesta not in ['s', 'si', 'y', 'yes', '']:
            print("\n⚠️  Operación cancelada")
            return 0
        
        print()
        print("=" * 80)
        print()
        
        # Configuración
        settings = Settings()
        
        # Crear scraper
        scraper = GolesDetalladosScraper(settings=settings)
        
        # Opciones de scraping
        print("Opciones de scraping:")
        print("  1. Todos los jugadores (recomendado)")
        print("  2. Limitar a N jugadores (para testing)")
        print()
        
        opcion = input("Selecciona una opción (1-2) [1]: ").strip() or "1"
        
        max_jugadores = None
        if opcion == "2":
            try:
                max_jugadores = int(input("¿Cuántos jugadores? (ej: 10): ").strip())
            except ValueError:
                print("⚠️  Valor inválido, procesando todos los jugadores")
        
        print()
        print("=" * 80)
        print()
        
        # Ejecutar scraping
        goles = scraper.scrape(max_jugadores=max_jugadores, paralelo=True)
        
        print()
        print("=" * 80)
        print(f"✅ ¡Scraping completado exitosamente!")
        print(f"📊 Total de jugadores en base de datos: {len(goles)}")
        total_goles_count = sum(j.total_goles for j in goles.values())
        print(f"⚽ Total de goles documentados: {total_goles_count}")
        print(f"💾 Archivo generado: {scraper.output_file}")
        print("=" * 80)
        print()
        
        # Sugerencias
        print("💡 Próximos pasos:")
        print("   • Ver datos: cat data/output/rosario_central_goles_detallados.json | jq")
        print("   • Buscar jugador: jq '.jugadores[\"Marco Ruben\"]' data/output/rosario_central_goles_detallados.json")
        print("   • Estructura: Jugadores agrupados por nombre (clave primaria)")
        print("   • Análisis: Importa el JSON en Python/R para análisis avanzados")
        print()
        
        return 0
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Programa interrumpido por el usuario")
        print("💾 Los goles scrapeados hasta ahora fueron guardados")
        return 1
    
    except Exception as e:
        print(f"\n❌ Error fatal: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
