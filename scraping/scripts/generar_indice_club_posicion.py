#!/usr/bin/env python3
"""
Script para generar índice optimizado por club y posición

Este índice permite búsquedas O(1) en lugar de O(n*m)

Input: rosario_central_jugadores.json
Output: club_posicion_index.json

Estructura:
{
  "Club Name": {
    "Position": [
      {
        "nombre": "Full Name",
        "apellido": "Surname",
        "otros_clubes": ["Club1", "Club2"],
        "posiciones": ["Pos1", "Pos2"],
        "image_profile": "path/to/image.jpg"
      }
    ]
  }
}
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any
from collections import defaultdict

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent


def normalizar_posicion(posicion: str) -> str:
    """
    Normaliza posiciones a las usadas en el juego
    """
    mapeo = {
        'portero': 'PO',
        'lateral derecho': 'ED',
        'defensa central': 'DC',
        'lateral izquierdo': 'EI',
        'pivote': 'MC',
        'mediocentro': 'MC',
        'mediocentro defensivo': 'MC',
        'interior derecho': 'MD',
        'interior izquierdo': 'MI',
        'mediocampista': 'MC',
        'mediocentro ofensivo': 'MO',
        'mediapunta': 'MO',
        'extremo derecho': 'ED',
        'extremo izquierdo': 'EI',
        'delantero centro': 'DEL',
        'segundo delantero': 'DEL'
    }
    
    pos_lower = posicion.lower().strip()
    return mapeo.get(pos_lower, posicion)


def generar_indice_club_posicion(
    jugadores_file: Path,
    output_file: Path
) -> Dict[str, Any]:
    """
    Genera índice optimizado agrupado por club y posición
    
    Args:
        jugadores_file: Path al archivo rosario_central_jugadores.json
        output_file: Path para guardar el índice generado
    
    Returns:
        Diccionario con estadísticas del proceso
    """
    print("🔄 Generando índice club-posición...")
    print(f"   📂 Input: {jugadores_file}")
    print(f"   📂 Output: {output_file}")
    
    # Load data
    with open(jugadores_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    jugadores = data.get('jugadores', [])
    print(f"   👥 Jugadores totales: {len(jugadores)}")
    
    # Build index
    index = defaultdict(lambda: defaultdict(list))
    
    jugadores_procesados = 0
    jugadores_con_rc = 0
    entradas_totales = 0
    
    for jugador in jugadores:
        jugadores_procesados += 1
        
        clubes_historia = jugador.get('clubes_historia', [])
        
        # Check if played in Rosario Central
        tiene_rc = any('rosario central' in c.get('nombre', '').lower() 
                      for c in clubes_historia)
        
        if not tiene_rc:
            continue
        
        jugadores_con_rc += 1
        
        # Extract relevant data
        nombre = jugador['nombre']
        apellido = jugador.get('apellido', nombre.split()[-1])
        posiciones = jugador.get('posiciones', [])
        image_profile = jugador.get('image_profile', '')
        
        # Get all clubs except Rosario Central
        otros_clubes = []
        clubes_jugador = []
        
        for club_hist in clubes_historia:
            club_nombre = club_hist.get('nombre', '')
            
            if 'rosario central' in club_nombre.lower():
                continue
            
            clubes_jugador.append(club_nombre)
            otros_clubes.append(club_nombre)
        
        # Remove duplicates while preserving order
        otros_clubes = list(dict.fromkeys(otros_clubes))
        clubes_jugador = list(dict.fromkeys(clubes_jugador))
        
        # Create player entry
        jugador_entry = {
            'nombre': nombre,
            'apellido': apellido,
            'otros_clubes': otros_clubes,
            'posiciones': posiciones,
            'image_profile': image_profile
        }
        
        # Add to index for each club and position
        for club_nombre in clubes_jugador:
            for posicion in posiciones:
                # Normalize position for game compatibility
                pos_normalizada = normalizar_posicion(posicion)
                
                # Add to index
                index[club_nombre][pos_normalizada].append(jugador_entry)
                entradas_totales += 1
    
    # Convert defaultdict to regular dict for JSON serialization
    index_json = {
        club: {
            pos: jugadores_list
            for pos, jugadores_list in posiciones.items()
        }
        for club, posiciones in index.items()
    }
    
    # Save to file
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(index_json, f, ensure_ascii=False, indent=2)
    
    # Statistics
    stats = {
        'jugadores_procesados': jugadores_procesados,
        'jugadores_con_rc': jugadores_con_rc,
        'clubes_en_indice': len(index_json),
        'entradas_totales': entradas_totales,
        'output_file': str(output_file)
    }
    
    print(f"\n✅ Índice generado exitosamente!")
    print(f"   👥 Jugadores procesados: {jugadores_procesados}")
    print(f"   ⚽ Jugadores con RC: {jugadores_con_rc}")
    print(f"   🏟️  Clubes en índice: {len(index_json)}")
    print(f"   📊 Entradas totales: {entradas_totales}")
    print(f"   💾 Tamaño archivo: {output_file.stat().st_size / 1024:.2f} KB")
    
    return stats


def main():
    """Main execution"""
    # Paths
    data_dir = PROJECT_ROOT / 'scraping' / 'data' / 'output'
    jugadores_file = data_dir / 'rosario_central_jugadores.json'
    output_file = data_dir / 'club_posicion_index.json'
    
    # Validate input exists
    if not jugadores_file.exists():
        print(f"❌ Error: No se encontró {jugadores_file}")
        sys.exit(1)
    
    # Generate index
    try:
        stats = generar_indice_club_posicion(jugadores_file, output_file)
        print(f"\n🎉 Proceso completado!")
        return 0
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
