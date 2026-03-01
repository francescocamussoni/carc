#!/usr/bin/env python3
"""
Análisis de temporadas útiles en rosario_central_tecnicos_jugadores.json

Muestra por cada temporada:
- Cantidad de jugadores únicos
- Total de partidos (apariciones)
- Total de minutos jugados
- Total de goles
- Técnicos que dirigieron
- Torneos jugados
"""

import json
from pathlib import Path
from collections import defaultdict

def main():
    # Cargar datos
    json_path = Path(__file__).parent.parent / "data" / "output" / "rosario_central_tecnicos_jugadores.json"
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Diccionario para agrupar por temporada
    temporadas_data = defaultdict(lambda: {
        'jugadores': set(),
        'partidos': 0,
        'minutos': 0,
        'goles': 0,
        'tecnicos': set(),
        'torneos': set(),
        'detalle_torneos': []
    })
    
    # Procesar todos los técnicos y sus torneos
    for tecnico_nombre, tecnico_info in data['tecnicos'].items():
        for torneo in tecnico_info.get('torneos', []):
            temporada = torneo['temporada']
            nombre_torneo = torneo['torneo']
            
            # Agregar datos de esta temporada
            temporadas_data[temporada]['tecnicos'].add(tecnico_nombre)
            temporadas_data[temporada]['torneos'].add(nombre_torneo)
            
            # Agregar detalle del torneo
            temporadas_data[temporada]['detalle_torneos'].append({
                'tecnico': tecnico_nombre,
                'torneo': nombre_torneo,
                'jugadores': torneo['total_jugadores']
            })
            
            # Procesar jugadores de este torneo
            for jugador in torneo.get('jugadores', []):
                temporadas_data[temporada]['jugadores'].add(jugador['nombre'])
                temporadas_data[temporada]['partidos'] += jugador.get('apariciones', 0)
                temporadas_data[temporada]['minutos'] += jugador.get('minutos', 0)
                temporadas_data[temporada]['goles'] += jugador.get('goles', 0)
    
    # Ordenar temporadas
    temporadas_ordenadas = sorted(temporadas_data.keys())
    
    # Mostrar resultados
    print("=" * 100)
    print("📊 ANÁLISIS DE TEMPORADAS - ROSARIO CENTRAL")
    print("=" * 100)
    print(f"\nTotal de temporadas registradas: {len(temporadas_ordenadas)}")
    print(f"Rango: {temporadas_ordenadas[0]} - {temporadas_ordenadas[-1]}")
    
    print("\n" + "=" * 100)
    print("DETALLE POR TEMPORADA")
    print("=" * 100)
    print(f"{'Temp':<8} {'Jugadores':<11} {'Partidos':<10} {'Minutos':<12} {'Goles':<8} {'Técnicos':<10} {'Torneos':<8}")
    print("-" * 100)
    
    # Estadísticas para promedios
    total_jugadores = 0
    total_partidos = 0
    total_minutos = 0
    total_goles = 0
    
    temporadas_completas = []  # Para identificar temporadas con buena info
    
    for temporada in temporadas_ordenadas:
        info = temporadas_data[temporada]
        num_jugadores = len(info['jugadores'])
        num_partidos = info['partidos']
        num_minutos = info['minutos']
        num_goles = info['goles']
        num_tecnicos = len(info['tecnicos'])
        num_torneos = len(info['torneos'])
        
        # Marcar temporadas "completas" (con buena cantidad de info)
        es_completa = num_partidos >= 100 and num_minutos >= 8000
        marca = "✅" if es_completa else "  "
        
        if es_completa:
            temporadas_completas.append(temporada)
        
        print(f"{temporada:<8} {num_jugadores:<11} {num_partidos:<10} {num_minutos:<12,} {num_goles:<8} {num_tecnicos:<10} {num_torneos:<8} {marca}")
        
        total_jugadores += num_jugadores
        total_partidos += num_partidos
        total_minutos += num_minutos
        total_goles += num_goles
    
    # Resumen
    print("-" * 100)
    print(f"{'PROMEDIO':<8} {total_jugadores/len(temporadas_ordenadas):<11.1f} {total_partidos/len(temporadas_ordenadas):<10.1f} {total_minutos/len(temporadas_ordenadas):<12,.0f} {total_goles/len(temporadas_ordenadas):<8.1f}")
    
    # Temporadas útiles
    print("\n" + "=" * 100)
    print("🎯 TEMPORADAS ÚTILES (≥100 partidos y ≥8,000 minutos)")
    print("=" * 100)
    print(f"\nTotal: {len(temporadas_completas)} temporadas")
    print(f"Lista: {', '.join(temporadas_completas)}")
    
    # Top 10 temporadas por cantidad de datos
    print("\n" + "=" * 100)
    print("🏆 TOP 10 TEMPORADAS CON MÁS INFORMACIÓN")
    print("=" * 100)
    
    temporadas_rankeadas = sorted(
        temporadas_ordenadas,
        key=lambda t: (temporadas_data[t]['partidos'], temporadas_data[t]['minutos']),
        reverse=True
    )[:10]
    
    print(f"\n{'#':<4} {'Temporada':<12} {'Partidos':<10} {'Minutos':<12} {'Goles':<8} {'Jugadores':<10}")
    print("-" * 100)
    
    for i, temporada in enumerate(temporadas_rankeadas, 1):
        info = temporadas_data[temporada]
        print(f"{i:<4} {temporada:<12} {info['partidos']:<10} {info['minutos']:<12,} {info['goles']:<8} {len(info['jugadores']):<10}")
    
    # Detalle de torneos por temporada útil (opcional, últimas 5 temporadas completas)
    print("\n" + "=" * 100)
    print("📋 DETALLE DE ÚLTIMAS 5 TEMPORADAS COMPLETAS")
    print("=" * 100)
    
    ultimas_completas = temporadas_completas[-5:] if len(temporadas_completas) >= 5 else temporadas_completas
    
    for temporada in ultimas_completas:
        info = temporadas_data[temporada]
        print(f"\n🗓️  {temporada}")
        print(f"   Jugadores: {len(info['jugadores'])}")
        print(f"   Partidos: {info['partidos']}")
        print(f"   Minutos: {info['minutos']:,}")
        print(f"   Goles: {info['goles']}")
        print(f"   Técnicos: {', '.join(sorted(info['tecnicos']))}")
        print(f"   Torneos: {', '.join(sorted(info['torneos']))}")
    
    print("\n" + "=" * 100)
    print("💡 LEYENDA")
    print("=" * 100)
    print("✅ = Temporada con información completa (≥100 partidos y ≥8,000 minutos)")
    print("\nLas temporadas marcadas con ✅ son ideales para generar el juego 'Órbita del Día'")
    print("=" * 100)

if __name__ == '__main__':
    main()
