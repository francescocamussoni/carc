#!/usr/bin/env python3
"""
Análisis de temporadas con información de técnicos-jugadores
"""
import json
from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime


def analyze_tecnicos_jugadores_temporadas():
    """Analiza las temporadas con información de técnicos-jugadores"""
    
    # Cargar datos
    data_path = Path(__file__).parent.parent / "data" / "output" / "rosario_central_tecnicos_jugadores.json"
    
    if not data_path.exists():
        print(f"❌ Archivo no encontrado: {data_path}")
        return
    
    with open(data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    tecnicos = data.get('tecnicos', {})
    
    # Análisis
    temporadas_por_tecnico = {}
    jugadores_por_temporada = Counter()
    torneos_por_temporada = Counter()
    total_registros = 0
    temporadas_globales = set()
    
    for tecnico_nombre, tecnico_data in tecnicos.items():
        torneos = tecnico_data.get('torneos', [])
        temporadas_tecnico = set()
        
        for torneo in torneos:
            temporada = torneo.get('temporada', 'Desconocida')
            torneo_nombre = torneo.get('torneo', 'Desconocido')
            jugadores = torneo.get('jugadores', [])
            num_jugadores = len(jugadores)
            
            temporadas_tecnico.add(temporada)
            temporadas_globales.add(temporada)
            jugadores_por_temporada[temporada] += num_jugadores
            torneos_por_temporada[temporada] += 1
            total_registros += num_jugadores
        
        temporadas_por_tecnico[tecnico_nombre] = temporadas_tecnico
    
    # Generar reporte
    print("=" * 80)
    print("👔 ANÁLISIS DE TÉCNICOS-JUGADORES POR TEMPORADA")
    print("=" * 80)
    print(f"\n📅 Fecha de análisis: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📁 Archivo analizado: {data_path.name}")
    print(f"\n📈 RESUMEN GENERAL:")
    print(f"   • Total de técnicos: {len(tecnicos)}")
    print(f"   • Total de temporadas únicas: {len(temporadas_globales)}")
    print(f"   • Total de registros jugador-torneo: {total_registros}")
    print(f"   • Promedio jugadores/temporada: {total_registros / len(temporadas_globales):.1f}")
    
    print(f"\n👔 TÉCNICOS POR TEMPORADAS DIRIGIDAS:\n")
    
    # Ordenar técnicos por número de temporadas
    tecnicos_ordenados = sorted(
        temporadas_por_tecnico.items(),
        key=lambda x: len(x[1]),
        reverse=True
    )
    
    for i, (tecnico, temporadas) in enumerate(tecnicos_ordenados, 1):
        print(f"{i:2d}. {tecnico:35s} - {len(temporadas):2d} temporadas")
        if len(temporadas) <= 10:
            print(f"     └─ {', '.join(sorted(temporadas))}")
        else:
            print(f"     └─ {', '.join(sorted(temporadas)[:10])} ...")
        print()
    
    # Análisis por temporada
    print("=" * 80)
    print("📅 JUGADORES REGISTRADOS POR TEMPORADA (Top 20)")
    print("=" * 80 + "\n")
    
    temporadas_ordenadas = jugadores_por_temporada.most_common(20)
    max_jugadores = max(jugadores_por_temporada.values())
    
    for i, (temporada, num_jugadores) in enumerate(temporadas_ordenadas, 1):
        # Barra de progreso visual
        barra_length = int(num_jugadores / max_jugadores * 40)
        barra = "█" * barra_length + "░" * (40 - barra_length)
        torneos = torneos_por_temporada[temporada]
        
        print(f"{i:2d}. {temporada:10s} │ {barra} │ {num_jugadores:3d} jugadores ({torneos} torneos)")
    
    # Análisis de cobertura temporal
    print("\n" + "=" * 80)
    print("📊 ANÁLISIS DE COBERTURA TEMPORAL")
    print("=" * 80 + "\n")
    
    # Extraer años y ordenar
    try:
        anos = sorted([int(t) for t in temporadas_globales if t.isdigit()])
        if anos:
            ano_min, ano_max = min(anos), max(anos)
            print(f"📆 Rango de años: {ano_min} - {ano_max}")
            print(f"📊 Span temporal: {ano_max - ano_min + 1} años")
            
            # Identificar períodos con buena cobertura (más de 15 jugadores)
            temporadas_buena_cobertura = [t for t, j in jugadores_por_temporada.items() if j >= 15]
            
            print(f"\n✅ Temporadas con buena cobertura (≥15 jugadores): {len(temporadas_buena_cobertura)}")
            if temporadas_buena_cobertura:
                print(f"   Temporadas: {', '.join(sorted(temporadas_buena_cobertura)[:20])}")
                if len(temporadas_buena_cobertura) > 20:
                    print(f"   ... y {len(temporadas_buena_cobertura) - 20} más")
            
            # Identificar brechas (años sin datos)
            anos_con_datos = set(anos)
            anos_completos = set(range(ano_min, ano_max + 1))
            anos_sin_datos = anos_completos - anos_con_datos
            
            if anos_sin_datos:
                print(f"\n⚠️  Años sin datos: {len(anos_sin_datos)}")
                if len(anos_sin_datos) <= 20:
                    print(f"   Años: {', '.join(map(str, sorted(anos_sin_datos)))}")
                else:
                    print(f"   Años: {', '.join(map(str, sorted(anos_sin_datos)[:20]))} ...")
            
            # Análisis por décadas
            print(f"\n📊 COBERTURA POR DÉCADAS:\n")
            
            decadas = defaultdict(list)
            for ano in anos:
                decada = (ano // 10) * 10
                decadas[decada].append(ano)
            
            for decada in sorted(decadas.keys()):
                anos_decada = decadas[decada]
                jugadores_decada = sum(jugadores_por_temporada[str(ano)] for ano in anos_decada if str(ano) in jugadores_por_temporada)
                
                print(f"   {decada}s: {len(anos_decada):2d} años con datos - {jugadores_decada:4d} registros totales")
    
    except Exception as e:
        print(f"⚠️  No se pudo analizar cobertura temporal: {e}")
    
    # Análisis de calidad de datos
    print("\n" + "=" * 80)
    print("🎯 ANÁLISIS DE CALIDAD DE DATOS")
    print("=" * 80 + "\n")
    
    # Revisar completitud de datos por técnico
    tecnicos_con_datos_completos = 0
    tecnicos_con_pocos_datos = []
    
    for tecnico_nombre, tecnico_data in tecnicos.items():
        torneos = tecnico_data.get('torneos', [])
        total_jugadores_tecnico = sum(len(t.get('jugadores', [])) for t in torneos)
        
        if total_jugadores_tecnico >= 30:  # Umbral de "datos completos"
            tecnicos_con_datos_completos += 1
        elif total_jugadores_tecnico < 15:
            tecnicos_con_pocos_datos.append((tecnico_nombre, total_jugadores_tecnico))
    
    print(f"✅ Técnicos con datos completos (≥30 jugadores): {tecnicos_con_datos_completos}")
    print(f"⚠️  Técnicos con datos limitados (<15 jugadores): {len(tecnicos_con_pocos_datos)}")
    
    if tecnicos_con_pocos_datos:
        print(f"\n   Técnicos con datos limitados:")
        for tecnico, num_jug in sorted(tecnicos_con_pocos_datos, key=lambda x: x[1])[:10]:
            print(f"   • {tecnico:30s} - {num_jug:2d} jugadores")
        if len(tecnicos_con_pocos_datos) > 10:
            print(f"   ... y {len(tecnicos_con_pocos_datos) - 10} más")
    
    print("\n" + "=" * 80)
    
    # Análisis de jugadores más dirigidos
    print("⭐ TOP 15 JUGADORES MÁS DIRIGIDOS (por diferentes técnicos)\n")
    
    jugadores_tecnicos = defaultdict(set)
    jugadores_apariciones = Counter()
    
    for tecnico_nombre, tecnico_data in tecnicos.items():
        for torneo in tecnico_data.get('torneos', []):
            for jugador in torneo.get('jugadores', []):
                nombre_jugador = jugador.get('nombre', 'Desconocido')
                jugadores_tecnicos[nombre_jugador].add(tecnico_nombre)
                jugadores_apariciones[nombre_jugador] += jugador.get('apariciones', 0)
    
    # Ordenar por número de técnicos que lo dirigieron
    jugadores_mas_dirigidos = sorted(
        jugadores_tecnicos.items(),
        key=lambda x: (len(x[1]), jugadores_apariciones[x[0]]),
        reverse=True
    )[:15]
    
    for i, (jugador, tecnicos_set) in enumerate(jugadores_mas_dirigidos, 1):
        apariciones = jugadores_apariciones[jugador]
        print(f"{i:2d}. {jugador:30s} - {len(tecnicos_set):2d} técnicos - {apariciones:3d} apariciones")
    
    print("\n" + "=" * 80)
    
    return {
        'total_tecnicos': len(tecnicos),
        'temporadas': len(temporadas_globales),
        'registros_totales': total_registros,
        'tecnicos_datos_completos': tecnicos_con_datos_completos
    }


if __name__ == '__main__':
    analyze_tecnicos_jugadores_temporadas()
