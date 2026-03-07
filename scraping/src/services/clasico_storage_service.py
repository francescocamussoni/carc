"""
Servicio de almacenamiento para partidos clásicos
Guarda en JSON optimizado para FastAPI
"""
import json
from pathlib import Path
from typing import Optional
from datetime import datetime

from src.models.partido_clasico import ClasicosCollection


class ClasicoStorageService:
    """Servicio para guardar y cargar partidos clásicos"""
    
    def __init__(self, output_dir: Path):
        """
        Inicializa el servicio de storage
        
        Args:
            output_dir: Directorio donde guardar los JSONs
        """
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def save_collection(
        self, 
        collection: ClasicosCollection, 
        filename: str = "rosario_central_clasicos.json"
    ) -> Path:
        """
        Guarda la colección de partidos en JSON
        
        Args:
            collection: Colección de partidos
            filename: Nombre del archivo
            
        Returns:
            Path al archivo guardado
        """
        output_path = self.output_dir / filename
        
        # Convertir a dict
        data = collection.to_dict()
        
        # Añadir metadata
        data['metadata'] = {
            'fecha_scraping': datetime.now().isoformat(),
            'total_partidos': len(collection.partidos),
            'version': '1.0.0'
        }
        
        # Guardar con pretty print
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Guardado: {output_path}")
        print(f"   Total partidos: {len(collection.partidos)}")
        print(f"   Tamaño: {output_path.stat().st_size / 1024:.1f} KB")
        
        return output_path
    
    def load_collection(
        self, 
        filename: str = "rosario_central_clasicos.json"
    ) -> Optional[ClasicosCollection]:
        """
        Carga la colección desde JSON
        
        Args:
            filename: Nombre del archivo
            
        Returns:
            ClasicosCollection o None si no existe
        """
        input_path = self.output_dir / filename
        
        if not input_path.exists():
            print(f"❌ No existe: {input_path}")
            return None
        
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Reconstruir colección (simplificado, no reconstruye objetos completos)
        collection = ClasicosCollection()
        collection.partidos = data.get('partidos', [])
        collection.total_partidos = len(collection.partidos)
        collection.ultima_actualizacion = data.get('ultima_actualizacion')
        
        print(f"✅ Cargado: {input_path}")
        print(f"   Total partidos: {len(collection.partidos)}")
        
        return collection
    
    def save_partidos_for_game(
        self,
        collection: ClasicosCollection,
        filename: str = "rosario_central_clasicos_game.json"
    ) -> Path:
        """
        Guarda solo los datos necesarios para el juego (optimizado)
        
        Incluye solo:
        - Partidos con formación completa
        - Datos mínimos necesarios para el juego
        - Optimizado para carga rápida en FastAPI
        
        Args:
            collection: Colección completa
            filename: Nombre del archivo
            
        Returns:
            Path al archivo guardado
        """
        output_path = self.output_dir / filename
        
        # Filtrar solo partidos con formación completa (11 titulares)
        partidos_validos = []
        
        for partido in collection.partidos:
            partido_dict = partido.to_dict()
            
            # Verificar que tenga formación completa
            if partido_dict.get('formacion') and \
               len(partido_dict['formacion'].get('jugadores_titulares', [])) == 11:
                
                # Crear versión simplificada para el juego
                partido_game = {
                    'partido_id': partido_dict['partido_id'],
                    'fecha': partido_dict['fecha'],
                    'competicion': partido_dict['competicion'],
                    'local': partido_dict['local'],
                    'visitante': partido_dict['visitante'],
                    'resultado': partido_dict['resultado'],
                    'goles_local': partido_dict['goles_local'],
                    'goles_visitante': partido_dict['goles_visitante'],
                    'rosario_central_local': partido_dict['rosario_central_local'],
                    
                    # Esquema táctico
                    'esquema': partido_dict['formacion']['esquema'],
                    
                    # Entrenador (solo apellido para adivinar)
                    'entrenador': {
                        'apellido': partido_dict['formacion']['entrenador']['apellido'],
                        'nombre_completo': partido_dict['formacion']['entrenador']['nombre_completo'],
                        'foto_url': partido_dict['formacion']['entrenador'].get('foto_url')
                    },
                    
                    # Jugadores titulares (solo apellidos para adivinar)
                    'jugadores': [
                        {
                            'numero': j['numero'],
                            'apellido': j['apellido'],
                            'nombre_completo': j['nombre_completo'],
                            'posicion': j['posicion'],
                            'foto_url': j.get('foto_url'),
                            'goles': j.get('goles', 0)
                        }
                        for j in partido_dict['formacion']['jugadores_titulares']
                    ],
                    
                    # Goles (para validación)
                    'goles_rosario_central': [
                        {
                            'jugador_apellido': g['jugador_apellido'],
                            'jugador_nombre_completo': g['jugador_nombre_completo'],
                            'minuto': g['minuto']
                        }
                        for g in partido_dict.get('goles', [])
                    ],
                    
                    # Árbitro
                    'arbitro': {
                        'apellido': partido_dict.get('arbitro', {}).get('apellido'),
                        'nombre_completo': partido_dict.get('arbitro', {}).get('nombre_completo')
                    } if partido_dict.get('arbitro') else None
                }
                
                partidos_validos.append(partido_game)
        
        # Crear estructura final
        game_data = {
            'partidos': partidos_validos,
            'total_partidos': len(partidos_validos),
            'metadata': {
                'fecha_generacion': datetime.now().isoformat(),
                'version': '1.0.0',
                'optimizado_para': 'game_api'
            }
        }
        
        # Guardar
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(game_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Guardado (optimizado para juego): {output_path}")
        print(f"   Partidos válidos: {len(partidos_validos)}")
        print(f"   Tamaño: {output_path.stat().st_size / 1024:.1f} KB")
        
        return output_path
    
    def generate_summary(self, collection: ClasicosCollection) -> dict:
        """
        Genera un resumen estadístico de la colección
        
        Returns:
            Dict con estadísticas
        """
        total = len(collection.partidos)
        con_formacion = sum(1 for p in collection.partidos if p.formacion_rosario_central)
        con_arbitro = sum(1 for p in collection.partidos if p.arbitro)
        total_goles = sum(len(p.goles_rosario_central) for p in collection.partidos)
        
        # Contar partidos por competición
        competiciones = {}
        for p in collection.partidos:
            comp = p.competicion
            competiciones[comp] = competiciones.get(comp, 0) + 1
        
        # Goleadores
        goleadores = {}
        for p in collection.partidos:
            for gol in p.goles_rosario_central:
                apellido = gol.jugador_apellido
                goleadores[apellido] = goleadores.get(apellido, 0) + 1
        
        top_goleadores = sorted(goleadores.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            'total_partidos': total,
            'partidos_con_formacion_completa': con_formacion,
            'partidos_con_arbitro': con_arbitro,
            'total_goles_rosario_central': total_goles,
            'competiciones': competiciones,
            'top_goleadores': dict(top_goleadores),
            'porcentaje_datos_completos': f"{(con_formacion / total * 100):.1f}%" if total > 0 else "0%"
        }
