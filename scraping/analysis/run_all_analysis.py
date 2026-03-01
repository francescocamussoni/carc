#!/usr/bin/env python3
"""
Script maestro para ejecutar todos los análisis de datos
"""
import sys
from pathlib import Path
from datetime import datetime

# Agregar el directorio actual al path
sys.path.insert(0, str(Path(__file__).parent))

from analyze_jugadores_clubes import analyze_jugadores_clubes
from analyze_tecnicos_clubes import analyze_tecnicos_clubes
from analyze_goles_detallados import analyze_goles_detallados
from analyze_tecnicos_jugadores_temporadas import analyze_tecnicos_jugadores_temporadas
from analyze_posiciones import analyze_posiciones


def print_header():
    """Imprime el encabezado del reporte"""
    print("\n")
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + " " * 20 + "ANÁLISIS DE DATOS - ROSARIO CENTRAL" + " " * 23 + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "═" * 78 + "╝")
    print(f"\n📅 Fecha de generación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🎯 Propósito: Evaluar calidad y cobertura de datos scrapeados\n")


def print_section_separator(title):
    """Imprime un separador de sección"""
    print("\n\n")
    print("╔" + "═" * 78 + "╗")
    print(f"║  {title}" + " " * (76 - len(title)) + "║")
    print("╚" + "═" * 78 + "╝")
    print()


def print_summary(results):
    """Imprime resumen consolidado de todos los análisis"""
    print_section_separator("📊 RESUMEN CONSOLIDADO")
    
    print("=" * 80)
    print("DATOS GENERALES")
    print("=" * 80 + "\n")
    
    print(f"👥 JUGADORES:")
    print(f"   • Total de jugadores: {results['jugadores']['total_jugadores']}")
    print(f"   • Con historial de clubes: {results['jugadores']['jugadores_con_historia']}")
    print(f"   • Países representados: {results['jugadores']['paises']}")
    
    print(f"\n👔 TÉCNICOS:")
    print(f"   • Total de técnicos: {results['tecnicos']['total_tecnicos']}")
    print(f"   • Con historial de clubes: {results['tecnicos']['tecnicos_con_historia']}")
    print(f"   • Países representados: {results['tecnicos']['paises']}")
    
    print(f"\n⚽ GOLES DETALLADOS:")
    print(f"   • Total de goles: {results['goles']['total_goles']}")
    print(f"   • Competiciones: {results['goles']['competiciones']}")
    print(f"   • Temporadas: {results['goles']['temporadas']}")
    print(f"   • Jugadores goleadores: {results['goles']['jugadores']}")
    
    print(f"\n🎯 TÉCNICOS-JUGADORES:")
    print(f"   • Técnicos analizados: {results['tecnicos_jugadores']['total_tecnicos']}")
    print(f"   • Temporadas cubiertas: {results['tecnicos_jugadores']['temporadas']}")
    print(f"   • Registros totales: {results['tecnicos_jugadores']['registros_totales']}")
    print(f"   • Técnicos con datos completos: {results['tecnicos_jugadores']['tecnicos_datos_completos']}")
    
    print(f"\n⚽ POSICIONES:")
    print(f"   • Posiciones únicas (jugadores): {results['posiciones']['posiciones_jugadores']}")
    print(f"   • Posiciones únicas (técnicos-jug): {results['posiciones']['posiciones_tj']}")
    print(f"   • Todas compatibles: {'✅ Sí' if results['posiciones']['posiciones_jugadores'] == results['posiciones']['posiciones_tj'] else '⚠️ No'}")
    
    # Recomendaciones
    print("\n" + "=" * 80)
    print("💡 RECOMENDACIONES PARA JUEGOS")
    print("=" * 80 + "\n")
    
    print("✅ JUEGOS VIABLES:")
    print("   1. 🇦🇷 Equipo Nacional del Día")
    print("      └─ Datos suficientes de jugadores argentinos por técnico")
    print()
    print("   2. ⚽ Órbita del Día")
    print("      └─ Buena cobertura de jugadores por técnico/temporada")
    print()
    
    if results['jugadores']['paises'] >= 5:
        print("   3. 🌍 Trayectoria Internacional (POSIBLE)")
        print("      └─ Múltiples países representados")
        print()
    
    print("⚠️  JUEGOS CON LIMITACIONES:")
    
    if results['tecnicos_jugadores']['tecnicos_datos_completos'] < 10:
        print("   • Equipo Internacional: Requiere más jugadores extranjeros")
        print("     └─ Considerar relajar requisitos (8-9 jugadores en vez de 11)")
        print()
    
    if results['goles']['temporadas'] < 20:
        print("   • Juegos basados en goleadores: Cobertura temporal limitada")
        print("     └─ Enfocarse en temporadas recientes con más datos")
        print()
    
    print("📈 PRÓXIMOS PASOS SUGERIDOS:")
    print("   1. Implementar juegos viables primero (Nacional, Órbita)")
    print("   2. Evaluar ajustar formaciones a 8-10 jugadores para mayor flexibilidad")
    print("   3. Priorizar temporadas 2010+ con mejor cobertura de datos")
    print("   4. Considerar agregar más scrapers para jugadores internacionales")
    
    print("\n" + "=" * 80)


def save_summary_to_file(results):
    """Guarda un resumen en archivo de texto"""
    output_path = Path(__file__).parent / "analysis_summary.txt"
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("RESUMEN DE ANÁLISIS - ROSARIO CENTRAL\n")
        f.write("=" * 80 + "\n")
        f.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("DATOS GENERALES\n")
        f.write("-" * 80 + "\n")
        f.write(f"Jugadores totales: {results['jugadores']['total_jugadores']}\n")
        f.write(f"Técnicos totales: {results['tecnicos']['total_tecnicos']}\n")
        f.write(f"Goles registrados: {results['goles']['total_goles']}\n")
        f.write(f"Temporadas T-J: {results['tecnicos_jugadores']['temporadas']}\n")
        f.write(f"Posiciones únicas: {results['posiciones']['posiciones_jugadores']}\n\n")
        
        f.write("COBERTURA GEOGRÁFICA\n")
        f.write("-" * 80 + "\n")
        f.write(f"Países (jugadores): {results['jugadores']['paises']}\n")
        f.write(f"Países (técnicos): {results['tecnicos']['paises']}\n\n")
        
        f.write("JUEGOS RECOMENDADOS\n")
        f.write("-" * 80 + "\n")
        f.write("✅ Equipo Nacional del Día\n")
        f.write("✅ Órbita del Día\n")
        f.write("⚠️  Equipo Internacional (limitado)\n")
    
    print(f"\n💾 Resumen guardado en: {output_path}")


def main():
    """Ejecuta todos los análisis"""
    print_header()
    
    results = {}
    
    try:
        # Análisis 1: Jugadores - Clubes
        print_section_separator("1/4: Análisis de Clubes por País (Jugadores)")
        results['jugadores'] = analyze_jugadores_clubes()
        
        input("\n⏸️  Presiona ENTER para continuar con el siguiente análisis...")
        
        # Análisis 2: Técnicos - Clubes
        print_section_separator("2/4: Análisis de Clubes por País (Técnicos)")
        results['tecnicos'] = analyze_tecnicos_clubes()
        
        input("\n⏸️  Presiona ENTER para continuar con el siguiente análisis...")
        
        # Análisis 3: Goles Detallados
        print_section_separator("3/4: Análisis de Goles Detallados por Temporada")
        results['goles'] = analyze_goles_detallados()
        
        input("\n⏸️  Presiona ENTER para continuar con el siguiente análisis...")
        
        # Análisis 4: Técnicos-Jugadores
        print_section_separator("4/5: Análisis de Técnicos-Jugadores por Temporada")
        results['tecnicos_jugadores'] = analyze_tecnicos_jugadores_temporadas()
        
        input("\n⏸️  Presiona ENTER para continuar con el siguiente análisis...")
        
        # Análisis 5: Posiciones
        print_section_separator("5/5: Análisis de Posiciones de Transfermarkt")
        results['posiciones'] = analyze_posiciones()
        
        # Resumen consolidado
        print_summary(results)
        
        # Guardar resumen
        save_summary_to_file(results)
        
        print("\n✅ Análisis completado exitosamente!\n")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Análisis interrumpido por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error durante el análisis: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
