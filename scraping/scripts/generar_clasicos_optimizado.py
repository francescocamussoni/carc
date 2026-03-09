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
        
        # ✅ Las posiciones ya vienen correctas del scraper de Transfermarkt
        # NO necesitamos inferirlas por el esquema
        
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
