"""
Script para ejecutar el scraper de jugadores dirigidos por técnicos.

Este script obtiene información detallada de todos los jugadores que cada técnico
dirigió en Rosario Central, agrupados por torneo y temporada.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import Settings
from src.scrapers.tecnico_jugadores_scraper import TecnicoJugadoresScraper


def print_banner():
    print()
    print("=" * 80)
    print("⚽ SCRAPER DE JUGADORES DIRIGIDOS POR TÉCNICOS")
    print("=" * 80)
    print()
    print("Este scraper obtiene información detallada de jugadores dirigidos por")
    print("cada técnico en Rosario Central:")
    print()
    print("  ✅ Agrupados por torneo y temporada")
    print("  ✅ Nombre, nacionalidad y posición del jugador")
    print("  ✅ Apariciones bajo ese técnico en ese torneo")
    print("  ✅ Goles y asistencias en ese torneo")
    print("  ✅ URL de perfil del jugador")
    print()


def print_info():
    print("ℹ️  Configuración:")
    print("   • Requiere: data/output/rosario_central_tecnicos.json")
    print("   • Guarda en: data/output/rosario_central_tecnicos_jugadores.json")
    print("   • Scraping incremental: Saltea técnicos ya procesados")
    print("   • Procesamiento paralelo: Hasta 10 workers simultáneos")
    print()
    print("⏱️  Tiempo estimado:")
    print("   • Por técnico: ~2-5 segundos (depende de torneos)")
    print("   • Total (43 técnicos): ~5-8 minutos")
    print()


def main():
    try:
        print_banner()
        print_info()
        
        respuesta = input("¿Deseas continuar? (s/n): ").strip().lower()
        if respuesta not in ['s', 'si', 'y', 'yes', '']:
            print("\n⚠️  Operación cancelada")
            return 0
        
        print()
        print("=" * 80)
        print()
        
        settings = Settings()
        scraper = TecnicoJugadoresScraper(settings=settings)
        
        print("Opciones de scraping:")
        print("  1. Todos los técnicos (recomendado)")
        print("  2. Limitar a N técnicos (para testing)")
        print()
        
        opcion = input("Selecciona una opción (1-2) [1]: ").strip() or "1"
        
        max_tecnicos = None
        if opcion == "2":
            try:
                max_tecnicos = int(input("¿Cuántos técnicos? (ej: 3): ").strip())
            except ValueError:
                print("⚠️  Valor inválido, procesando todos los técnicos")
        
        print()
        print("=" * 80)
        print()
        
        # Ejecutar scraper
        tecnicos_jugadores = scraper.scrape(max_tecnicos=max_tecnicos, paralelo=True)
        
        # Mostrar resumen final
        print()
        print("=" * 80)
        print(f"✅ ¡Scraping completado exitosamente!")
        print(f"📊 Total de técnicos con jugadores: {len(tecnicos_jugadores)}")
        
        total_torneos = sum(len(t.torneos) for t in tecnicos_jugadores.values())
        total_jugadores = 0
        for tecnico in tecnicos_jugadores.values():
            for torneo in tecnico.torneos:
                total_jugadores += len(torneo.jugadores)
        
        print(f"🏆 Total de torneos: {total_torneos}")
        print(f"⚽ Total de registros jugador-torneo: {total_jugadores}")
        print(f"💾 Archivo generado: {scraper.output_file}")
        print("=" * 80)
        print()
        
        print("💡 Próximos pasos:")
        print("   • Ver datos: cat data/output/rosario_central_tecnicos_jugadores.json | jq")
        print("   • Buscar técnico: jq '.tecnicos[\"Miguel Ángel Russo\"]' data/output/rosario_central_tecnicos_jugadores.json")
        print("   • Buscar torneo: jq '.tecnicos[\"Miguel Ángel Russo\"].torneos[0]' data/output/rosario_central_tecnicos_jugadores.json")
        print("   • Estructura: Técnicos → Torneos → Jugadores con estadísticas")
        print()
        
        return 0
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Programa interrumpido por el usuario")
        print("💾 Los datos scrapeados hasta ahora fueron guardados")
        return 1
    
    except Exception as e:
        print(f"❌ Error fatal: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
