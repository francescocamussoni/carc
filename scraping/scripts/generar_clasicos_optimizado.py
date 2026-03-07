#!/usr/bin/env python3
"""
Script para generar un índice optimizado de partidos clásicos
Combina rosario_central_clasicos.json + rosario_central_jugadores.json
para incluir historial de clubes de cada jugador (necesario para pistas)
"""

import json
import unicodedata
from pathlib import Path
from typing import Dict, List, Optional


def normalize_name(name: str) -> str:
    """Normalize name for comparison (remove accents, lowercase)"""
    if not name:
        return ""
    nfd = unicodedata.normalize('NFD', name)
    without_accents = ''.join(char for char in nfd if unicodedata.category(char) != 'Mn')
    return without_accents.lower().strip()


def find_jugador_by_name(apellido: str, nombre: str, jugadores_db: List[Dict]) -> Optional[Dict]:
    """
    Find a player in the jugadores database by surname and name
    Uses fuzzy matching to handle variations
    """
    apellido_norm = normalize_name(apellido)
    nombre_norm = normalize_name(nombre)
    
    # First try: exact match on apellido
    for jugador in jugadores_db:
        jug_apellido = jugador.get('apellido', '')
        jug_nombre = jugador.get('nombre', '')
        
        if normalize_name(jug_apellido) == apellido_norm:
            # Check if nombre matches or is contained
            if normalize_name(jug_nombre) == nombre_norm or nombre_norm in normalize_name(jug_nombre):
                return jugador
    
    # Second try: check in nombre_completo
    nombre_completo_norm = normalize_name(f"{nombre} {apellido}")
    for jugador in jugadores_db:
        jug_nombre_completo = jugador.get('nombre_completo', '')
        if normalize_name(jug_nombre_completo) == nombre_completo_norm:
            return jugador
    
    # Third try: apellido contained in nombre_completo
    for jugador in jugadores_db:
        jug_nombre_completo = jugador.get('nombre_completo', '')
        if apellido_norm in normalize_name(jug_nombre_completo):
            return jugador
    
    return None


def extract_clubes_from_jugador(jugador: Dict) -> List[str]:
    """Extract all club names from player's history"""
    clubes = []
    
    # From clubes_historia
    for club_entry in jugador.get('clubes_historia', []):
        # Try both 'nombre' and 'club_nombre' keys
        club_nombre = club_entry.get('nombre', club_entry.get('club_nombre', ''))
        if club_nombre and club_nombre != 'Rosario Central':
            clubes.append(club_nombre)
    
    # Remove duplicates while preserving order
    seen = set()
    clubes_unicos = []
    for club in clubes:
        if club not in seen:
            seen.add(club)
            clubes_unicos.append(club)
    
    return clubes_unicos


def assign_positions_by_formation(esquema: str, jugadores: List[Dict]) -> List[Dict]:
    """
    Asigna posiciones correctas según el esquema táctico y el orden de los jugadores.
    Los jugadores vienen en orden de formación desde portero hasta delanteros.
    
    Args:
        esquema: Esquema táctico (ej: "4-3-3", "4-4-2", "4-2-3-1")
        jugadores: Lista de 11 jugadores titulares en orden
        
    Returns:
        Lista de jugadores con posiciones correctamente asignadas
    """
    if len(jugadores) != 11:
        print(f"⚠️  Se esperaban 11 jugadores, se recibieron {len(jugadores)}")
        return jugadores
    
    # Parse el esquema (ej: "4-3-3" -> [4, 3, 3], "4-2-3-1" -> [4, 2, 3, 1])
    try:
        lineas = [int(x) for x in esquema.split('-')]
    except:
        print(f"⚠️  Esquema inválido: {esquema}")
        return jugadores
    
    # El primer jugador siempre es el portero
    jugadores[0]['posicion'] = 'PO'
    idx = 1
    
    # Línea defensiva
    if len(lineas) >= 1:
        num_defensores = lineas[0]
        if num_defensores == 4:
            # 4 defensores: EI, DC, DC, ED
            jugadores[idx]['posicion'] = 'EI'
            jugadores[idx + 1]['posicion'] = 'DC'
            jugadores[idx + 2]['posicion'] = 'DC'
            jugadores[idx + 3]['posicion'] = 'ED'
        elif num_defensores == 3:
            # 3 defensores: DC, DC, DC (o EI, DC, ED para 3-5-2)
            jugadores[idx]['posicion'] = 'DC'
            jugadores[idx + 1]['posicion'] = 'DC'
            jugadores[idx + 2]['posicion'] = 'DC'
        elif num_defensores == 5:
            # 5 defensores: EI, DC, DC, DC, ED
            jugadores[idx]['posicion'] = 'EI'
            jugadores[idx + 1]['posicion'] = 'DC'
            jugadores[idx + 2]['posicion'] = 'DC'
            jugadores[idx + 3]['posicion'] = 'DC'
            jugadores[idx + 4]['posicion'] = 'ED'
        idx += num_defensores
    
    # Detectar si es formación de 3 o 4 líneas (sin contar portero)
    num_lineas = len(lineas)
    
    if num_lineas == 4:
        # Formación con 4 líneas (ej: 4-2-3-1, 4-1-4-1)
        # Línea 2: Pivotes/Mediocampistas defensivos
        num_pivotes = lineas[1]
        for i in range(num_pivotes):
            jugadores[idx + i]['posicion'] = 'MC'
        idx += num_pivotes
        
        # Línea 3: Mediocampistas ofensivos/extremos
        num_medio_ofensivos = lineas[2]
        if num_medio_ofensivos == 3:
            # 3 mediapuntas: MI, MO, MD
            jugadores[idx]['posicion'] = 'MI'
            jugadores[idx + 1]['posicion'] = 'MO'
            jugadores[idx + 2]['posicion'] = 'MD'
        elif num_medio_ofensivos == 4:
            # 4 mediapuntas: MI, MO, MO, MD
            jugadores[idx]['posicion'] = 'MI'
            jugadores[idx + 1]['posicion'] = 'MO'
            jugadores[idx + 2]['posicion'] = 'MO'
            jugadores[idx + 3]['posicion'] = 'MD'
        elif num_medio_ofensivos == 2:
            # 2 mediapuntas: MO, MO
            jugadores[idx]['posicion'] = 'MO'
            jugadores[idx + 1]['posicion'] = 'MO'
        elif num_medio_ofensivos == 1:
            # 1 mediapunta: MO
            jugadores[idx]['posicion'] = 'MO'
        idx += num_medio_ofensivos
        
        # Línea 4: Delanteros
        num_delanteros = lineas[3]
        for i in range(num_delanteros):
            jugadores[idx + i]['posicion'] = 'DEL'
    
    else:
        # Formación con 3 líneas (ej: 4-3-3, 4-4-2, 3-5-2)
        # Línea media
        if len(lineas) >= 2:
            num_medios = lineas[1]
            if num_medios == 3:
                # 3 medios: MI, MC, MD
                jugadores[idx]['posicion'] = 'MI'
                jugadores[idx + 1]['posicion'] = 'MC'
                jugadores[idx + 2]['posicion'] = 'MD'
            elif num_medios == 4:
                # 4 medios: MI, MC, MC, MD
                jugadores[idx]['posicion'] = 'MI'
                jugadores[idx + 1]['posicion'] = 'MC'
                jugadores[idx + 2]['posicion'] = 'MC'
                jugadores[idx + 3]['posicion'] = 'MD'
            elif num_medios == 2:
                # 2 medios: MC, MC
                jugadores[idx]['posicion'] = 'MC'
                jugadores[idx + 1]['posicion'] = 'MC'
            elif num_medios == 5:
                # 5 medios: MI, MC, MC, MC, MD
                jugadores[idx]['posicion'] = 'MI'
                jugadores[idx + 1]['posicion'] = 'MC'
                jugadores[idx + 2]['posicion'] = 'MC'
                jugadores[idx + 3]['posicion'] = 'MC'
                jugadores[idx + 4]['posicion'] = 'MD'
            idx += num_medios
        
        # Línea delantera
        if len(lineas) >= 3:
            num_delanteros = lineas[2]
            if num_delanteros == 3:
                # 3 delanteros: DEL, DEL, DEL (todos delanteros)
                jugadores[idx]['posicion'] = 'DEL'
                jugadores[idx + 1]['posicion'] = 'DEL'
                jugadores[idx + 2]['posicion'] = 'DEL'
            elif num_delanteros == 2:
                # 2 delanteros: DEL, DEL
                jugadores[idx]['posicion'] = 'DEL'
                jugadores[idx + 1]['posicion'] = 'DEL'
            elif num_delanteros == 1:
                # 1 delantero: DEL
                jugadores[idx]['posicion'] = 'DEL'
            elif num_delanteros == 4:
                # 4 delanteros: DEL, DEL, DEL, DEL
                jugadores[idx]['posicion'] = 'DEL'
                jugadores[idx + 1]['posicion'] = 'DEL'
                jugadores[idx + 2]['posicion'] = 'DEL'
                jugadores[idx + 3]['posicion'] = 'DEL'
    
    return jugadores


def main():
    # Paths
    base_path = Path(__file__).parent.parent
    clasicos_path = base_path / "data/output/rosario_central_clasicos.json"
    jugadores_path = base_path / "data/output/rosario_central_jugadores.json"
    output_path = base_path / "data/output/rosario_central_clasicos_game.json"
    
    print("🔵⚪ Generando índice optimizado de clásicos para juego...")
    print()
    
    # Load data
    print("📂 Cargando datos...")
    with open(clasicos_path, 'r', encoding='utf-8') as f:
        clasicos_data = json.load(f)
    
    with open(jugadores_path, 'r', encoding='utf-8') as f:
        jugadores_data = json.load(f)
    
    jugadores_db = jugadores_data.get('jugadores', [])
    print(f"   ✅ {len(clasicos_data.get('partidos', []))} partidos clásicos")
    print(f"   ✅ {len(jugadores_db)} jugadores en DB")
    print()
    
    # Process each partido
    print("⚙️  Procesando partidos...")
    partidos_optimizados = []
    stats = {
        'total': 0,
        'jugadores_encontrados': 0,
        'jugadores_no_encontrados': 0,
        'con_clubes': 0,
        'sin_clubes': 0
    }
    
    for partido in clasicos_data.get('partidos', []):
        stats['total'] += 1
        
        # Get formacion
        formacion = partido.get('formacion', {})
        jugadores_titulares = formacion.get('jugadores_titulares', [])
        
        # Enrich each jugador with clubes history
        jugadores_enriquecidos = []
        for jugador in jugadores_titulares:
            apellido = jugador.get('apellido', '')
            nombre = jugador.get('nombre', '')
            
            # Find in DB
            jugador_db = find_jugador_by_name(apellido, nombre, jugadores_db)
            
            if jugador_db:
                stats['jugadores_encontrados'] += 1
                otros_clubes = extract_clubes_from_jugador(jugador_db)
                
                if otros_clubes:
                    stats['con_clubes'] += 1
                else:
                    stats['sin_clubes'] += 1
                
                # Create enriched player
                # Buscar foto: primero en jugadores_db, luego en clasicos
                foto_url = jugador_db.get('image_profile') or jugador.get('foto_url')
                
                jugador_enriquecido = {
                    'apellido': apellido,
                    'nombre_completo': jugador.get('nombre_completo', f"{nombre} {apellido}"),
                    'posicion': jugador.get('posicion', 'MC'),
                    'numero': jugador.get('numero', 0),
                    'foto_url': foto_url,
                    'image_url': foto_url,  # Para compatibilidad con frontend
                    'goles': jugador.get('goles', 0),
                    'otros_clubes': otros_clubes,
                    'posiciones': jugador_db.get('posiciones', []),
                }
                jugadores_enriquecidos.append(jugador_enriquecido)
            else:
                stats['jugadores_no_encontrados'] += 1
                # Keep basic info even if not found
                jugadores_enriquecidos.append({
                    'apellido': apellido,
                    'nombre_completo': jugador.get('nombre_completo', f"{nombre} {apellido}"),
                    'posicion': jugador.get('posicion', 'MC'),
                    'numero': jugador.get('numero', 0),
                    'foto_url': jugador.get('foto_url'),
                    'image_url': jugador.get('foto_url'),  # Para compatibilidad con frontend
                    'goles': jugador.get('goles', 0),
                    'otros_clubes': [],
                    'posiciones': [],
                })
                print(f"   ⚠️  No encontrado: {apellido} ({nombre})")
        
        # Assign correct positions based on formation scheme
        esquema = formacion.get('esquema', '4-3-3')
        jugadores_enriquecidos = assign_positions_by_formation(esquema, jugadores_enriquecidos)
        
        # Create optimized partido
        entrenador = formacion.get('entrenador', {})
        arbitro = partido.get('arbitro', {})
        
        partido_optimizado = {
            'partido_id': partido.get('partido_id'),
            'fecha': partido.get('fecha'),
            'competicion': partido.get('competicion'),
            'local': partido.get('local'),
            'visitante': partido.get('visitante'),
            'resultado': partido.get('resultado'),
            'goles_local': partido.get('goles_local', 0),
            'goles_visitante': partido.get('goles_visitante', 0),
            'rosario_central_local': partido.get('rosario_central_local', False),
            'esquema': formacion.get('esquema', '4-3-3'),
            'entrenador': {
                'apellido': entrenador.get('apellido', ''),
                'nombre_completo': entrenador.get('nombre_completo', ''),
                'foto_url': entrenador.get('foto_url'),
                'image_url': entrenador.get('foto_url'),  # Para compatibilidad con frontend
            },
            'arbitro': {
                'apellido': arbitro.get('apellido', ''),
                'nombre_completo': arbitro.get('nombre_completo', ''),
            },
            'jugadores': jugadores_enriquecidos
        }
        
        partidos_optimizados.append(partido_optimizado)
    
    print(f"   ✅ Procesados {stats['total']} partidos")
    print()
    
    # Save output
    print("💾 Guardando archivo optimizado...")
    output_data = {
        'partidos': partidos_optimizados,
        'metadata': {
            'total_partidos': len(partidos_optimizados),
            'generado': 'generar_clasicos_optimizado.py',
            'descripcion': 'Partidos clásicos optimizados para juego con historial de clubes'
        }
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print(f"   ✅ Guardado en: {output_path}")
    print()
    
    # Print stats
    print("📊 Estadísticas:")
    print(f"   • Total partidos: {stats['total']}")
    print(f"   • Jugadores encontrados: {stats['jugadores_encontrados']}")
    print(f"   • Jugadores NO encontrados: {stats['jugadores_no_encontrados']}")
    print(f"   • Con clubes: {stats['con_clubes']}")
    print(f"   • Sin clubes: {stats['sin_clubes']}")
    print()
    
    print("✅ ¡Listo! Archivo optimizado generado exitosamente.")


if __name__ == '__main__':
    main()
