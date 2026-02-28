#!/usr/bin/env python3
"""
Script para scrappear técnicos de Rosario Central
"""

import sys
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import Settings
from src.scrapers.tecnico_scraper import TecnicoScraper


def print_banner():
    """Imprime el banner de inicio"""
    print()
    print("=" * 80)
    print("👔 SCRAPER DE TÉCNICOS - ROSARIO CENTRAL")
    print("=" * 80)
    print()
    print("Este scraper obtiene información completa de los técnicos/entrenadores")
    print("que dirigieron Rosario Central:")
    print()
    print("  ✅ Nombre y nacionalidad")
    print("  ✅ Fecha de nacimiento y edad")
    print("  ✅ Foto de perfil")
    print("  ✅ Periodo en Rosario Central")
    print("  ✅ Todos los clubes que dirigió (con país y periodo)")
    print("  ✅ Estadísticas por torneo (partidos, victorias, empates, derrotas)")
    print()


def print_info():
    """Imprime información adicional"""
    print("ℹ️  Configuración:")
    print("   • Guarda en: data/output/rosario_central_tecnicos.json")
    print("   • Fotos en: data/images/tecnicos/")
    print("   • Scraping incremental: Saltea técnicos ya procesados")
    print("   • Procesamiento paralelo: Hasta 10 workers simultáneos")
    print()
    print("⏱️  Tiempo estimado:")
    print("   • ~2-3 segundos por técnico (optimizado)")
    print("   • 65 técnicos: ~3-4 minutos")
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
        scraper = TecnicoScraper(settings=settings)
        
        # Opciones de scraping
        print("Opciones de scraping:")
        print("  1. Todos los técnicos (recomendado)")
        print("  2. Limitar a N técnicos (para testing)")
        print()
        
        opcion = input("Selecciona una opción (1-2) [1]: ").strip() or "1"
        
        max_tecnicos = None
        if opcion == "2":
            try:
                max_tecnicos = int(input("¿Cuántos técnicos? (ej: 5): ").strip())
            except ValueError:
                print("⚠️  Valor inválido, procesando todos los técnicos")
        
        print()
        print("=" * 80)
        print()
        
        # Ejecutar scraping
        tecnicos = scraper.scrape(max_tecnicos=max_tecnicos, paralelo=True)
        
        print()
        print("=" * 80)
        print(f"✅ ¡Scraping completado exitosamente!")
        print(f"📊 Total de técnicos en base de datos: {len(tecnicos)}")
        total_partidos = sum(t.info_rosario.total_partidos for t in tecnicos.values())
        total_periodos = sum(t.info_rosario.total_periodos for t in tecnicos.values())
        tecnicos_multiples = sum(1 for t in tecnicos.values() if t.info_rosario.total_periodos > 1)
        print(f"⚽ Total de partidos dirigidos: {total_partidos}")
        print(f"📅 Total de periodos: {total_periodos}")
        print(f"🔄 Técnicos con múltiples pasos: {tecnicos_multiples}")
        print(f"💾 Archivo generado: {scraper.output_file}")
        print("=" * 80)
        print()
        
        # Sugerencias
        print("💡 Próximos pasos:")
        print("   • Ver datos: cat data/output/rosario_central_tecnicos.json | jq")
        print("   • Buscar técnico: jq '.tecnicos[\"Carlos Tevez\"]' data/output/rosario_central_tecnicos.json")
        print("   • Estructura: Técnicos agrupados por nombre (clave primaria)")
        print("   • Scraper detallado: python scripts/run_tecnicos_detallados.py")
        print()
        
        return 0
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Programa interrumpido por el usuario")
        print("💾 Los técnicos scrapeados hasta ahora fueron guardados")
        return 1
    
    except Exception as e:
        print(f"\n❌ Error fatal: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
