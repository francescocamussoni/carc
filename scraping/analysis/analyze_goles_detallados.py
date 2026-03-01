#!/usr/bin/env python3
"""
Análisis de temporadas con información de goles detallados
"""
import json
from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime


def analyze_goles_detallados():
    """Analiza las temporadas con información de goles detallados"""
    
    # Cargar datos
    data_path = Path(__file__).parent.parent / "data" / "output" / "rosario_central_goles_detallados.json"
    
    if not data_path.exists():
        print(f"❌ Archivo no encontrado: {data_path}")
        return
    
    with open(data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    goles_por_competicion = data.get('goles_por_competicion', {})
    
    # Análisis
    temporadas_por_competicion = defaultdict(set)
    goles_por_temporada = Counter()
    jugadores_goleadores = set()
    total_goles = 0
    
    for competicion, comp_data in goles_por_competicion.items():
        goles = comp_data.get('goles', [])
        
        for gol in goles:
            temporada = gol.get('temporada', 'Desconocida')
            jugador = gol.get('jugador', 'Desconocido')
            
            temporadas_por_competicion[competicion].add(temporada)
            goles_por_temporada[temporada] += 1
            jugadores_goleadores.add(jugador)
            total_goles += 1
    
    # Generar reporte
    print("=" * 80)
    print("⚽ ANÁLISIS DE GOLES DETALLADOS POR TEMPORADA")
    print("=" * 80)
    print(f"\n📅 Fecha de análisis: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📁 Archivo analizado: {data_path.name}")
    print(f"\n📈 RESUMEN GENERAL:")
    print(f"   • Total de competiciones: {len(goles_por_competicion)}")
    print(f"   • Total de goles registrados: {total_goles}")
    print(f"   • Jugadores goleadores únicos: {len(jugadores_goleadores)}")
    print(f"   • Temporadas con datos: {len(goles_por_temporada)}")
    
    print(f"\n🏆 GOLES POR COMPETICIÓN:\n")
    
    # Ordenar competiciones por número de goles
    competiciones_ordenadas = sorted(
        goles_por_competicion.items(),
        key=lambda x: len(x[1].get('goles', [])),
        reverse=True
    )
    
    for i, (competicion, comp_data) in enumerate(competiciones_ordenadas, 1):
        num_goles = len(comp_data.get('goles', []))
        temporadas = temporadas_por_competicion[competicion]
        
        print(f"{i:2d}. {competicion}")
        print(f"     └─ Goles: {num_goles}")
        print(f"     └─ Temporadas: {len(temporadas)}")
        print(f"     └─ Años: {', '.join(sorted(temporadas)[:10])}")
        if len(temporadas) > 10:
            print(f"              ... y {len(temporadas) - 10} más")
        print()
    
    # Análisis por temporada
    print("=" * 80)
    print("📅 GOLES POR TEMPORADA (Top 20)")
    print("=" * 80 + "\n")
    
    temporadas_ordenadas = goles_por_temporada.most_common(20)
    
    for i, (temporada, num_goles) in enumerate(temporadas_ordenadas, 1):
        # Barra de progreso visual
        barra_length = int(num_goles / max(goles_por_temporada.values()) * 40)
        barra = "█" * barra_length + "░" * (40 - barra_length)
        
        print(f"{i:2d}. {temporada:10s} │ {barra} │ {num_goles:3d} goles")
    
    # Análisis de cobertura temporal
    print("\n" + "=" * 80)
    print("📊 ANÁLISIS DE COBERTURA TEMPORAL")
    print("=" * 80 + "\n")
    
    # Extraer años y ordenar
    try:
        anos = sorted([int(t.split('/')[0]) for t in goles_por_temporada.keys() if '/' in t])
        if anos:
            ano_min, ano_max = min(anos), max(anos)
            print(f"📆 Rango de años: {ano_min} - {ano_max}")
            print(f"📊 Span temporal: {ano_max - ano_min + 1} años")
            
            # Identificar períodos con buena cobertura (más de 20 goles por temporada)
            temporadas_buena_cobertura = [t for t, g in goles_por_temporada.items() if g >= 20]
            
            print(f"\n✅ Temporadas con buena cobertura (≥20 goles): {len(temporadas_buena_cobertura)}")
            print(f"   Temporadas: {', '.join(sorted(temporadas_buena_cobertura)[:15])}")
            if len(temporadas_buena_cobertura) > 15:
                print(f"   ... y {len(temporadas_buena_cobertura) - 15} más")
            
            # Identificar brechas (años sin datos)
            anos_con_datos = set(anos)
            anos_completos = set(range(ano_min, ano_max + 1))
            anos_sin_datos = anos_completos - anos_con_datos
            
            if anos_sin_datos:
                print(f"\n⚠️  Años sin datos de goles: {len(anos_sin_datos)}")
                print(f"   Años: {', '.join(map(str, sorted(anos_sin_datos)))}")
            
            # Calcular promedio de goles por año
            promedio_goles = total_goles / len(anos_con_datos)
            print(f"\n📊 Promedio de goles por año: {promedio_goles:.1f}")
    
    except Exception as e:
        print(f"⚠️  No se pudo analizar cobertura temporal: {e}")
    
    print("\n" + "=" * 80)
    
    # Análisis de jugadores top goleadores
    print("🎯 TOP 10 GOLEADORES\n")
    
    jugadores_goles = Counter()
    for comp_data in goles_por_competicion.values():
        for gol in comp_data.get('goles', []):
            jugador = gol.get('jugador', 'Desconocido')
            jugadores_goles[jugador] += 1
    
    for i, (jugador, num_goles) in enumerate(jugadores_goles.most_common(10), 1):
        print(f"{i:2d}. {jugador:30s} - {num_goles:3d} goles")
    
    print("\n" + "=" * 80)
    
    return {
        'total_goles': total_goles,
        'competiciones': len(goles_por_competicion),
        'temporadas': len(goles_por_temporada),
        'jugadores': len(jugadores_goleadores)
    }


if __name__ == '__main__':
    analyze_goles_detallados()
