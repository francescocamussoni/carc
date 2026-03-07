#!/usr/bin/env python3
"""
Script para ejecutar el scraper de partidos clásicos Rosario Central vs Newell's Old Boys

Uso:
    python scripts/run_clasico.py                # Todos los partidos
    python scripts/run_clasico.py --limite 10    # Solo 10 partidos
    python scripts/run_clasico.py --test         # Solo 3 partidos (test)
"""
import sys
import argparse
from pathlib import Path
from datetime import datetime

# Añadir el directorio raíz al path
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.scrapers.clasico_scraper import ClasicoScraper
from src.services.clasico_storage_service import ClasicoStorageService


def main():
    """Función principal"""
    parser = argparse.ArgumentParser(
        description='Scraper de partidos clásicos Rosario Central vs Newell\'s Old Boys'
    )
    parser.add_argument(
        '--limite',
        type=int,
        default=None,
        help='Límite de partidos a scrapear (default: todos)'
    )
    parser.add_argument(
        '--test',
        action='store_true',
        help='Modo test: solo scrapea 3 partidos'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='data/output',
        help='Directorio de salida (default: data/output)'
    )
    
    args = parser.parse_args()
    
    # Banner
    print()
    print("=" * 80)
    print("🔵⚪ SCRAPER DE PARTIDOS CLÁSICOS")
    print("    Rosario Central vs Newell's Old Boys")
    print("=" * 80)
    print()
    
    # Configuración
    limite = 3 if args.test else args.limite
    output_dir = ROOT_DIR / args.output_dir
    
    print(f"📊 Configuración:")
    print(f"   Límite: {'Sin límite' if limite is None else f'{limite} partidos'}")
    print(f"   Output: {output_dir}")
    print()
    
    # Confirmación (excepto en modo test o con límite)
    if not args.test and limite is None:
        respuesta = input("¿Continuar? (s/n): ").strip().lower()
        if respuesta != 's':
            print("❌ Cancelado por el usuario")
            return 1
        print()
    
    # Iniciar tiempo
    inicio = datetime.now()
    
    # 1. Scrapear partidos
    print("🔍 Iniciando scraping...")
    print()
    
    scraper = ClasicoScraper()
    
    try:
        collection = scraper.scrape_all_clasicos(limite=limite)
        
        if not collection.partidos:
            print("❌ No se pudieron scrapear partidos")
            return 1
        
        # 2. Guardar resultados
        print()
        print("💾 Guardando resultados...")
        print()
        
        storage = ClasicoStorageService(output_dir)
        
        # Guardar colección completa
        storage.save_collection(collection)
        
        # Guardar versión optimizada para el juego
        storage.save_partidos_for_game(collection)
        
        # 3. Generar resumen
        print()
        print("=" * 80)
        print("📊 RESUMEN DE SCRAPING")
        print("=" * 80)
        print()
        
        resumen = storage.generate_summary(collection)
        
        print(f"✅ Partidos scrapeados:           {resumen['total_partidos']}")
        print(f"✅ Partidos con formación:        {resumen['partidos_con_formacion_completa']}")
        print(f"✅ Partidos con árbitro:          {resumen['partidos_con_arbitro']}")
        print(f"✅ Total goles RC:                {resumen['total_goles_rosario_central']}")
        print(f"✅ Datos completos:               {resumen['porcentaje_datos_completos']}")
        print()
        
        # Competiciones
        print("🏆 Partidos por competición:")
        for comp, cantidad in sorted(resumen['competiciones'].items(), key=lambda x: x[1], reverse=True):
            print(f"   {comp}: {cantidad}")
        print()
        
        # Top goleadores
        if resumen['top_goleadores']:
            print("⚽ Top 10 Goleadores en clásicos:")
            for i, (goleador, goles) in enumerate(resumen['top_goleadores'].items(), 1):
                print(f"   {i}. {goleador}: {goles} goles")
            print()
        
        # Tiempo total
        fin = datetime.now()
        duracion = (fin - inicio).total_seconds()
        print(f"⏱️  Tiempo total: {duracion:.1f}s ({duracion/60:.1f} min)")
        print()
        
        # Archivos generados
        print("📁 Archivos generados:")
        print(f"   1. rosario_central_clasicos.json (datos completos)")
        print(f"   2. rosario_central_clasicos_game.json (optimizado para juego)")
        print()
        
        print("=" * 80)
        print("🎉 ¡Scraping completado exitosamente!")
        print("=" * 80)
        print()
        
        return 0
    
    except KeyboardInterrupt:
        print()
        print("⚠️  Scraping interrumpido por el usuario")
        return 1
    
    except Exception as e:
        print()
        print(f"❌ Error durante el scraping: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
