#!/usr/bin/env python3
"""
Análisis de clubes por país en datos de técnicos
"""
import json
from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime


def analyze_tecnicos_clubes():
    """Analiza los clubes por país de los técnicos"""
    
    # Cargar datos
    data_path = Path(__file__).parent.parent / "data" / "output" / "rosario_central_tecnicos.json"
    
    if not data_path.exists():
        print(f"❌ Archivo no encontrado: {data_path}")
        return
    
    with open(data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    tecnicos = data.get('tecnicos', {})
    
    # Análisis
    clubes_por_pais = defaultdict(set)
    tecnicos_por_pais = Counter()
    tecnicos_con_historia_completa = 0
    
    for tecnico_nombre, tecnico_data in tecnicos.items():
        clubes_historia = tecnico_data.get('clubes_dirigidos', [])
        
        if clubes_historia:
            tecnicos_con_historia_completa += 1
        
        for club_data in clubes_historia:
            pais = club_data.get('pais', 'Desconocido')
            club_nombre = club_data.get('nombre', 'Desconocido')
            
            clubes_por_pais[pais].add(club_nombre)
            tecnicos_por_pais[pais] += 1
    
    # Generar reporte
    print("=" * 80)
    print("📊 ANÁLISIS DE CLUBES POR PAÍS - TÉCNICOS")
    print("=" * 80)
    print(f"\n📅 Fecha de análisis: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📁 Archivo analizado: {data_path.name}")
    print(f"\n📈 RESUMEN GENERAL:")
    print(f"   • Total de técnicos: {len(tecnicos)}")
    print(f"   • Técnicos con historial de clubes: {tecnicos_con_historia_completa}")
    print(f"   • Países con clubes registrados: {len(clubes_por_pais)}")
    print(f"   • Total de clubes únicos: {sum(len(clubes) for clubes in clubes_por_pais.values())}")
    
    print(f"\n🌎 CLUBES POR PAÍS (ordenado por cantidad de clubes):\n")
    
    # Ordenar países por cantidad de clubes
    paises_ordenados = sorted(clubes_por_pais.items(), key=lambda x: len(x[1]), reverse=True)
    
    for i, (pais, clubes) in enumerate(paises_ordenados, 1):
        num_tecnicos = tecnicos_por_pais[pais]
        print(f"{i:2d}. {pais:20s} - {len(clubes):3d} clubes - {num_tecnicos:3d} menciones")
        
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
    
    # Identificar países con más de 3 clubes (buena cobertura para técnicos)
    paises_buena_cobertura = [pais for pais, clubes in clubes_por_pais.items() if len(clubes) >= 3]
    
    print(f"\n✅ Países con buena cobertura (≥3 clubes): {len(paises_buena_cobertura)}")
    for pais in paises_buena_cobertura:
        print(f"   • {pais}: {len(clubes_por_pais[pais])} clubes")
    
    print("\n" + "=" * 80)
    
    return {
        'total_tecnicos': len(tecnicos),
        'tecnicos_con_historia': tecnicos_con_historia_completa,
        'paises': len(clubes_por_pais),
        'clubes_por_pais': {pais: len(clubes) for pais, clubes in clubes_por_pais.items()}
    }


if __name__ == '__main__':
    analyze_tecnicos_clubes()
