#!/usr/bin/env python3
"""
Análisis de posiciones de jugadores en Transfermarkt
"""
import json
from pathlib import Path
from collections import Counter
from datetime import datetime


def analyze_posiciones():
    """Analiza todas las posiciones únicas de jugadores"""
    
    print("=" * 80)
    print("⚽ ANÁLISIS DE POSICIONES DE JUGADORES - TRANSFERMARKT")
    print("=" * 80)
    print(f"\n📅 Fecha de análisis: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Cargar datos de jugadores
    jugadores_path = Path(__file__).parent.parent / "data" / "output" / "rosario_central_jugadores.json"
    
    posiciones_jugadores = Counter()
    total_jugadores = 0
    jugadores_sin_posicion = 0
    
    if jugadores_path.exists():
        print(f"📁 Analizando: {jugadores_path.name}\n")
        
        with open(jugadores_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        jugadores = data.get('jugadores', [])
        total_jugadores = len(jugadores)
        
        for jugador in jugadores:
            posicion = jugador.get('posicion', None)
            if posicion:
                posiciones_jugadores[posicion] += 1
            else:
                jugadores_sin_posicion += 1
    
    # Cargar datos de técnicos-jugadores
    tecnicos_jugadores_path = Path(__file__).parent.parent / "data" / "output" / "rosario_central_tecnicos_jugadores.json"
    
    posiciones_tecnicos_jugadores = Counter()
    total_registros_tj = 0
    registros_sin_posicion_tj = 0
    
    if tecnicos_jugadores_path.exists():
        print(f"📁 Analizando: {tecnicos_jugadores_path.name}\n")
        
        with open(tecnicos_jugadores_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        tecnicos = data.get('tecnicos', {})
        
        for tecnico_data in tecnicos.values():
            for torneo in tecnico_data.get('torneos', []):
                for jugador in torneo.get('jugadores', []):
                    total_registros_tj += 1
                    posicion = jugador.get('posicion', None)
                    if posicion:
                        posiciones_tecnicos_jugadores[posicion] += 1
                    else:
                        registros_sin_posicion_tj += 1
    
    # Reporte de jugadores
    print("=" * 80)
    print("📊 POSICIONES EN ARCHIVO DE JUGADORES")
    print("=" * 80)
    print(f"\n📈 RESUMEN:")
    print(f"   • Total de jugadores: {total_jugadores}")
    print(f"   • Con posición definida: {total_jugadores - jugadores_sin_posicion}")
    print(f"   • Sin posición: {jugadores_sin_posicion}")
    print(f"   • Posiciones únicas: {len(posiciones_jugadores)}")
    
    print(f"\n⚽ POSICIONES ENCONTRADAS (ordenadas por frecuencia):\n")
    
    # Agrupar por tipo de posición
    porteros = []
    defensas = []
    mediocampistas = []
    delanteros = []
    otras = []
    
    for posicion, count in posiciones_jugadores.most_common():
        pos_lower = posicion.lower()
        
        if any(x in pos_lower for x in ['portero', 'arquero', 'goalkeeper', 'keeper']):
            porteros.append((posicion, count))
        elif any(x in pos_lower for x in ['defensa', 'lateral', 'zaguero', 'líbero', 'libero', 'back', 'defender']):
            defensas.append((posicion, count))
        elif any(x in pos_lower for x in ['medio', 'volante', 'pivote', 'interior', 'midfielder', 'centro']):
            mediocampistas.append((posicion, count))
        elif any(x in pos_lower for x in ['delantero', 'extremo', 'punta', 'atacante', 'forward', 'striker', 'winger']):
            delanteros.append((posicion, count))
        else:
            otras.append((posicion, count))
    
    # Mostrar por categorías
    if porteros:
        print("🥅 PORTEROS:")
        for pos, count in porteros:
            porcentaje = (count / total_jugadores) * 100
            barra = "█" * int(porcentaje)
            print(f"   {pos:30s} │ {barra:20s} │ {count:3d} ({porcentaje:5.1f}%)")
        print()
    
    if defensas:
        print("🛡️  DEFENSAS:")
        for pos, count in defensas:
            porcentaje = (count / total_jugadores) * 100
            barra = "█" * int(porcentaje)
            print(f"   {pos:30s} │ {barra:20s} │ {count:3d} ({porcentaje:5.1f}%)")
        print()
    
    if mediocampistas:
        print("⚙️  MEDIOCAMPISTAS:")
        for pos, count in mediocampistas:
            porcentaje = (count / total_jugadores) * 100
            barra = "█" * int(porcentaje)
            print(f"   {pos:30s} │ {barra:20s} │ {count:3d} ({porcentaje:5.1f}%)")
        print()
    
    if delanteros:
        print("⚡ DELANTEROS:")
        for pos, count in delanteros:
            porcentaje = (count / total_jugadores) * 100
            barra = "█" * int(porcentaje)
            print(f"   {pos:30s} │ {barra:20s} │ {count:3d} ({porcentaje:5.1f}%)")
        print()
    
    if otras:
        print("❓ OTRAS POSICIONES:")
        for pos, count in otras:
            porcentaje = (count / total_jugadores) * 100
            print(f"   {pos:30s} │ {count:3d} ({porcentaje:5.1f}%)")
        print()
    
    # Reporte de técnicos-jugadores
    print("=" * 80)
    print("📊 POSICIONES EN ARCHIVO DE TÉCNICOS-JUGADORES")
    print("=" * 80)
    print(f"\n📈 RESUMEN:")
    print(f"   • Total de registros: {total_registros_tj}")
    print(f"   • Con posición definida: {total_registros_tj - registros_sin_posicion_tj}")
    print(f"   • Sin posición: {registros_sin_posicion_tj}")
    print(f"   • Posiciones únicas: {len(posiciones_tecnicos_jugadores)}")
    
    print(f"\n⚽ TOP 30 POSICIONES MÁS FRECUENTES:\n")
    
    for i, (posicion, count) in enumerate(posiciones_tecnicos_jugadores.most_common(30), 1):
        porcentaje = (count / total_registros_tj) * 100
        barra_length = int(porcentaje * 2)  # Escala la barra
        barra = "█" * barra_length + "░" * (40 - barra_length)
        print(f"{i:2d}. {posicion:30s} │ {barra} │ {count:4d} ({porcentaje:5.1f}%)")
    
    # Comparación entre archivos
    print("\n" + "=" * 80)
    print("🔄 COMPARACIÓN ENTRE ARCHIVOS")
    print("=" * 80 + "\n")
    
    posiciones_solo_jugadores = set(posiciones_jugadores.keys()) - set(posiciones_tecnicos_jugadores.keys())
    posiciones_solo_tj = set(posiciones_tecnicos_jugadores.keys()) - set(posiciones_jugadores.keys())
    posiciones_comunes = set(posiciones_jugadores.keys()) & set(posiciones_tecnicos_jugadores.keys())
    
    print(f"✅ Posiciones en ambos archivos: {len(posiciones_comunes)}")
    print(f"📄 Solo en jugadores.json: {len(posiciones_solo_jugadores)}")
    print(f"📄 Solo en tecnicos_jugadores.json: {len(posiciones_solo_tj)}")
    
    if posiciones_solo_jugadores:
        print(f"\n⚠️  Posiciones únicas en jugadores.json:")
        for pos in sorted(posiciones_solo_jugadores):
            print(f"   • {pos} ({posiciones_jugadores[pos]} jugadores)")
    
    if posiciones_solo_tj:
        print(f"\n⚠️  Posiciones únicas en tecnicos_jugadores.json:")
        for pos in sorted(list(posiciones_solo_tj)[:20]):  # Mostrar solo las primeras 20
            print(f"   • {pos} ({posiciones_tecnicos_jugadores[pos]} registros)")
        if len(posiciones_solo_tj) > 20:
            print(f"   ... y {len(posiciones_solo_tj) - 20} más")
    
    # Análisis de mapeo para el juego
    print("\n" + "=" * 80)
    print("🎮 MAPEO RECOMENDADO PARA JUEGOS")
    print("=" * 80 + "\n")
    
    print("Basado en el análisis, se recomienda el siguiente mapeo:\n")
    
    mapeo = {
        "PORTERO (PO)": [],
        "DEFENSA CENTRAL (DC)": [],
        "LATERAL DERECHO (ED)": [],
        "LATERAL IZQUIERDO (EI)": [],
        "MEDIOCAMPISTA CENTRAL (MC)": [],
        "INTERIOR DERECHO (MD)": [],
        "INTERIOR IZQUIERDO (MI)": [],
        "DELANTERO (CT)": []
    }
    
    for posicion in posiciones_jugadores.keys():
        pos_lower = posicion.lower()
        
        if any(x in pos_lower for x in ['portero', 'arquero', 'goalkeeper']):
            mapeo["PORTERO (PO)"].append(posicion)
        elif 'defensa central' in pos_lower or 'zaguero central' in pos_lower or pos_lower == 'defensa':
            mapeo["DEFENSA CENTRAL (DC)"].append(posicion)
        elif 'lateral derecho' in pos_lower or 'carrilero derecho' in pos_lower:
            mapeo["LATERAL DERECHO (ED)"].append(posicion)
        elif 'lateral izquierdo' in pos_lower or 'carrilero izquierdo' in pos_lower:
            mapeo["LATERAL IZQUIERDO (EI)"].append(posicion)
        elif 'mediocentro' in pos_lower or 'pivote' in pos_lower or 'medio defensivo' in pos_lower:
            mapeo["MEDIOCAMPISTA CENTRAL (MC)"].append(posicion)
        elif 'interior derecho' in pos_lower or 'medio derecho' in pos_lower:
            mapeo["INTERIOR DERECHO (MD)"].append(posicion)
        elif 'interior izquierdo' in pos_lower or 'medio izquierdo' in pos_lower:
            mapeo["INTERIOR IZQUIERDO (MI)"].append(posicion)
        elif any(x in pos_lower for x in ['delantero', 'extremo', 'punta', 'atacante']):
            mapeo["DELANTERO (CT)"].append(posicion)
    
    for categoria, posiciones in mapeo.items():
        if posiciones:
            print(f"{categoria}:")
            for pos in sorted(posiciones):
                count = posiciones_jugadores[pos]
                print(f"   • {pos} ({count} jugadores)")
            print()
    
    # Guardar todas las posiciones únicas a archivo
    output_path = Path(__file__).parent / "posiciones_unicas.txt"
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("POSICIONES ÚNICAS - TRANSFERMARKT\n")
        f.write("=" * 80 + "\n")
        f.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("ARCHIVO: rosario_central_jugadores.json\n")
        f.write("-" * 80 + "\n")
        for posicion, count in posiciones_jugadores.most_common():
            f.write(f"{posicion:40s} - {count:3d} jugadores\n")
        
        f.write("\n\n")
        f.write("ARCHIVO: rosario_central_tecnicos_jugadores.json\n")
        f.write("-" * 80 + "\n")
        for posicion, count in posiciones_tecnicos_jugadores.most_common():
            f.write(f"{posicion:40s} - {count:4d} registros\n")
    
    print("=" * 80)
    print(f"\n💾 Lista completa guardada en: {output_path}")
    print("\n✅ Análisis completado!\n")
    
    return {
        'posiciones_jugadores': len(posiciones_jugadores),
        'posiciones_tj': len(posiciones_tecnicos_jugadores),
        'total_jugadores': total_jugadores,
        'total_registros_tj': total_registros_tj
    }


if __name__ == '__main__':
    analyze_posiciones()
