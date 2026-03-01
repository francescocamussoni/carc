#!/usr/bin/env python3
"""
Análisis de clubes por país en datos de jugadores
"""
import json
from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime


def analyze_jugadores_clubes():
    """Analiza los clubes por país de los jugadores"""
    
    # Cargar datos
    data_path = Path(__file__).parent.parent / "data" / "output" / "rosario_central_jugadores.json"
    
    if not data_path.exists():
        print(f"❌ Archivo no encontrado: {data_path}")
        return
    
    with open(data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    jugadores = data.get('jugadores', [])
    
    # Análisis
    clubes_por_pais = defaultdict(set)
    jugadores_por_pais = Counter()
    jugadores_con_historia_completa = 0
    
    for jugador in jugadores:
        clubes_historia = jugador.get('clubes_historia', [])
        
        if clubes_historia:
            jugadores_con_historia_completa += 1
        
        for club_data in clubes_historia:
            pais = club_data.get('pais', 'Desconocido')
            club_nombre = club_data.get('nombre', 'Desconocido')
            
            clubes_por_pais[pais].add(club_nombre)
            jugadores_por_pais[pais] += 1
    
    # Generar reporte
    print("=" * 80)
    print("📊 ANÁLISIS DE CLUBES POR PAÍS - JUGADORES")
    print("=" * 80)
    print(f"\n📅 Fecha de análisis: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📁 Archivo analizado: {data_path.name}")
    print(f"\n📈 RESUMEN GENERAL:")
    print(f"   • Total de jugadores: {len(jugadores)}")
    print(f"   • Jugadores con historial de clubes: {jugadores_con_historia_completa}")
    print(f"   • Países con clubes registrados: {len(clubes_por_pais)}")
    print(f"   • Total de clubes únicos: {sum(len(clubes) for clubes in clubes_por_pais.values())}")
    
    print(f"\n🌎 CLUBES POR PAÍS (ordenado por cantidad de clubes):\n")
    
    # Ordenar países por cantidad de clubes
    paises_ordenados = sorted(clubes_por_pais.items(), key=lambda x: len(x[1]), reverse=True)
    
    for i, (pais, clubes) in enumerate(paises_ordenados, 1):
        num_jugadores = jugadores_por_pais[pais]
        print(f"{i:2d}. {pais:20s} - {len(clubes):3d} clubes - {num_jugadores:3d} menciones")
        
        # Mostrar algunos clubes de ejemplo (máximo 5)
        if len(clubes) <= 5:
            for club in sorted(clubes):
                print(f"     └─ {club}")
        else:
            clubes_muestra = sorted(list(clubes))[:5]
            for club in clubes_muestra:
                print(f"     └─ {club}")
            print(f"     └─ ... y {len(clubes) - 5} más")
        print()
    
    # Análisis de cobertura
    print("=" * 80)
    print("📊 ANÁLISIS DE COBERTURA")
    print("=" * 80)
    
    argentina_clubes = len(clubes_por_pais.get('Argentina', set()))
    extranjero_clubes = sum(len(clubes) for pais, clubes in clubes_por_pais.items() if pais != 'Argentina')
    
    print(f"\n🇦🇷 Clubes argentinos: {argentina_clubes}")
    print(f"🌍 Clubes extranjeros: {extranjero_clubes}")
    print(f"📊 Ratio ARG/EXT: {argentina_clubes}/{extranjero_clubes}")
    
    # Identificar países con más de 5 clubes (buena cobertura)
    paises_buena_cobertura = [pais for pais, clubes in clubes_por_pais.items() if len(clubes) >= 5]
    
    print(f"\n✅ Países con buena cobertura (≥5 clubes): {len(paises_buena_cobertura)}")
    for pais in paises_buena_cobertura:
        print(f"   • {pais}: {len(clubes_por_pais[pais])} clubes")
    
    print("\n" + "=" * 80)
    
    # Guardar lista completa de clubes por país en archivo de texto
    output_path = Path(__file__).parent / "clubes_por_pais_jugadores.txt"
    
    print(f"\n💾 Guardando lista completa de clubes por país en: {output_path.name}")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("CLUBES POR PAÍS - JUGADORES DE ROSARIO CENTRAL\n")
        f.write("=" * 80 + "\n")
        f.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total de países: {len(clubes_por_pais)}\n")
        f.write(f"Total de clubes únicos: {sum(len(clubes) for clubes in clubes_por_pais.values())}\n")
        f.write("=" * 80 + "\n\n")
        
        # Ordenar países por cantidad de clubes
        paises_ordenados = sorted(clubes_por_pais.items(), key=lambda x: len(x[1]), reverse=True)
        
        for i, (pais, clubes) in enumerate(paises_ordenados, 1):
            num_menciones = jugadores_por_pais[pais]
            f.write(f"\n{i}. {pais.upper()}\n")
            f.write(f"   Total de clubes: {len(clubes)}\n")
            f.write(f"   Menciones totales: {num_menciones}\n")
            f.write("-" * 80 + "\n")
            
            # Listar todos los clubes alfabéticamente
            for club in sorted(clubes):
                f.write(f"   • {club}\n")
            
            f.write("\n")
        
        f.write("=" * 80 + "\n")
        f.write("FIN DEL REPORTE\n")
        f.write("=" * 80 + "\n")
    
    print(f"✅ Archivo guardado exitosamente!")
    print(f"   Ubicación: {output_path}")
    print(f"   Tamaño: {output_path.stat().st_size:,} bytes")
    
    return {
        'total_jugadores': len(jugadores),
        'jugadores_con_historia': jugadores_con_historia_completa,
        'paises': len(clubes_por_pais),
        'clubes_por_pais': {pais: len(clubes) for pais, clubes in clubes_por_pais.items()}
    }


if __name__ == '__main__':
    analyze_jugadores_clubes()
