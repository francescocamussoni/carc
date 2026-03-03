"""
Service to generate daily games
Nueva mecánica: Mostrar club -> Usuario adivina jugador que jugó en RC + ese club
"""
import random
import json
import unicodedata
from datetime import datetime, date
from typing import Dict, List, Any, Optional, Set, Tuple
from pathlib import Path
from app.core.config import settings
from app.services.data_loader import data_loader_service
from app.schemas.game import (
    EquipoDelDiaGame,
    PosicionVacia,
    ClubActual
)


class GameGeneratorService:
    """Generates daily games with deterministic randomness based on date"""
    
    
    def __init__(self):
        self.data_loader = data_loader_service
        self.clubes_data = self._load_clubes()
        self.formaciones_data = self._load_formaciones()
        # Cache de juegos activos por game_id
        self._games_cache: Dict[str, Dict] = {}
        # Cache de formaciones usadas por día (para no repetir)
        self._formaciones_usadas_hoy: Set[str] = set()
    
    @staticmethod
    def _normalize_text(text: str) -> str:
        """
        Normalize text by removing accents/tildes and converting to lowercase
        
        Examples:
            'Ángel Di María' -> 'angel di maria'
            'Pérez' -> 'perez'
            'José' -> 'jose'
        """
        if not text:
            return ""
        # Convert to NFD (decomposed) form, then remove combining characters (accents)
        nfd = unicodedata.normalize('NFD', text)
        without_accents = ''.join(char for char in nfd if unicodedata.category(char) != 'Mn')
        return without_accents.lower()
    
    def _load_clubes(self) -> Dict:
        """Load clubes.json file"""
        clubes_path = Path(settings.CLUBES_FILE)
        with open(clubes_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _load_formaciones(self) -> Dict:
        """Load formaciones.json file"""
        formaciones_path = Path(settings.FORMACIONES_FILE)
        with open(formaciones_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _get_all_clubs_by_category(self, categoria: str) -> Set[str]:
        """Get all club names for a category"""
        clubs = set()
        for pais, clubes_list in self.clubes_data.get(categoria, {}).items():
            clubs.update(clubes_list)
        return clubs
    
    def _get_daily_seed(self, game_type: str) -> int:
        """Generate seed based on current date and game type"""
        today = date.today()
        type_offset = hash(game_type) % 1000
        return int(today.strftime("%Y%m%d")) + type_offset
    
    def _get_game_id(self, game_type: str) -> str:
        """Generate unique game ID for today"""
        today = date.today()
        return f"{game_type}_{today.strftime('%Y%m%d')}"
    
    def _normalize_position(self, pos: str) -> List[str]:
        """
        Get possible game positions for a Transfermarkt position using formaciones.json considerations
        """
        pos_lower = pos.lower().strip()
        
        # Build a combined map from all formations' considerations
        posiciones_resultado = set()
        
        for formacion_nombre, formacion_data in self.formaciones_data['formaciones'].items():
            consideraciones = formacion_data.get('consideraciones', {})
            
            # Check for exact match
            for tm_pos, game_pos in consideraciones.items():
                if tm_pos.lower() == pos_lower:
                    posiciones_resultado.add(game_pos)
        
        # If we found matches, return them
        if posiciones_resultado:
            return list(posiciones_resultado)
        
        # Fallback: partial match
        if 'porter' in pos_lower or 'arquer' in pos_lower:
            return ['PO']
        elif 'defens' in pos_lower and 'central' in pos_lower:
            return ['DC']
        elif 'lateral' in pos_lower:
            if 'derech' in pos_lower:
                return ['ED']
            elif 'izquier' in pos_lower:
                return ['EI']
            return ['ED', 'EI']
        elif 'defens' in pos_lower:
            return ['DC']
        elif 'medio' in pos_lower or 'volante' in pos_lower:
            if 'ofensivo' in pos_lower:
                return ['MC_ofensivo', 'MC']
            if 'derech' in pos_lower:
                return ['MD', 'MC']
            elif 'izquier' in pos_lower:
                return ['MI', 'MC']
            return ['MC']
        elif 'delant' in pos_lower or 'atac' in pos_lower:
            return ['DC_delantero']
        
        return ['MC']  # Default
    
    def _get_all_valid_positions(self, jugador: Dict) -> List[str]:
        """
        Get all valid game positions for a player based on their positions list
        
        Args:
            jugador: Player dict with 'posiciones' (list) or 'posicion' (string)
            
        Returns:
            List of all valid game positions (without duplicates)
        """
        todas_posiciones = set()
        
        # Try to get positions list first
        posiciones_lista = jugador.get('posiciones', [])
        if posiciones_lista:
            for pos in posiciones_lista:
                todas_posiciones.update(self._normalize_position(pos))
        
        # Fallback to single position field
        if not todas_posiciones:
            posicion_single = jugador.get('posicion', 'MC')
            todas_posiciones.update(self._normalize_position(posicion_single))
        
        return list(todas_posiciones)
    
    def _get_club_country(self, club_nombre: str) -> Optional[str]:
        """
        Get the country of a club from clubes.json
        
        Args:
            club_nombre: Name of the club
            
        Returns:
            Country name or None
        """
        for categoria, paises in self.clubes_data.items():
            for pais, clubes_list in paises.items():
                if club_nombre in clubes_list:
                    return pais
        return None
    
    def _get_jugador_image_url(self, jugador: Dict) -> Optional[str]:
        """
        Get player image URL
        
        Args:
            jugador: Player dict with 'image_profile' field
            
        Returns:
            URL path to player image or None
        """
        image_profile = jugador.get('image_profile')
        if not image_profile:
            return None
        
        # image_profile format: "data/images/jugadores/nombre_apellido.png"
        # We need to convert to: "/api/v1/static/jugadores/nombre_apellido.png"
        if image_profile.startswith('data/images/'):
            # Remove 'data/images/' prefix
            relative_path = image_profile.replace('data/images/', '')
            return f"/api/v1/static/{relative_path}"
        
        return None
    
    def _get_tecnico_image_url(self, tecnico_info: Dict) -> Optional[str]:
        """
        Get coach image URL
        
        Args:
            tecnico_info: Coach dict with 'image_profile' field
            
        Returns:
            URL path to coach image or None
        """
        image_profile = tecnico_info.get('image_profile')
        if not image_profile:
            return None
        
        # image_profile format: "data/images/tecnicos/nombre_apellido.jpeg"
        # We need to convert to: "/api/v1/static/tecnicos/nombre_apellido.jpeg"
        if image_profile.startswith('data/images/'):
            # Remove 'data/images/' prefix
            relative_path = image_profile.replace('data/images/', '')
            return f"/api/v1/static/{relative_path}"
        
        return None
    
    def _get_logo_url(self, club_nombre: str, pais: Optional[str] = None) -> Optional[str]:
        """
        Get club logo URL from country-specific subfolder
        
        Args:
            club_nombre: Name of the club
            pais: Country of the club (will be auto-detected if not provided)
            
        Returns:
            URL path to logo or None
        """
        # Auto-detect country if not provided
        if not pais:
            pais = self._get_club_country(club_nombre)
        
        if not pais:
            return None
        
        # Normalize club name for filename
        filename = club_nombre.lower()
        filename = filename.replace(' ', '_')
        filename = filename.replace('.', '')
        filename = filename.replace('-', '_')
        
        # Normalize country name for folder
        pais_folder = pais.lower().replace(' ', '_').replace('.', '')
        
        # Try different extensions in country subfolder
        for ext in ['png', 'jpg', 'jpeg', 'svg']:
            logo_path = Path(settings.IMAGES_DIR) / 'clubes' / pais_folder / f"{filename}.{ext}"
            if logo_path.exists():
                return f"/api/v1/static/clubes/{pais_folder}/{filename}.{ext}"
        
        # Fallback: try root clubes folder (for backwards compatibility)
        for ext in ['png', 'jpg', 'jpeg', 'svg']:
            logo_path = Path(settings.IMAGES_DIR) / 'clubes' / f"{filename}.{ext}"
            if logo_path.exists():
                return f"/api/v1/static/clubes/{filename}.{ext}"
        
        return None
    
    def _get_jugadores_con_clubes(self, clubs_permitidos: Set[str]) -> List[Dict]:
        """Get players who played in Rosario Central AND in allowed clubs"""
        jugadores = self.data_loader.get_all_jugadores()
        result = []
        
        for jugador in jugadores:
            clubes_historia = jugador.get('clubes_historia', [])
            
            # Check if played in Rosario Central
            tiene_rc = any('rosario central' in c.get('nombre', '').lower() 
                          for c in clubes_historia)
            
            if not tiene_rc:
                continue
            
            # Get clubs that are in the permitted list
            clubes_validos = [
                c['nombre'] for c in clubes_historia
                if c['nombre'] in clubs_permitidos and 
                'rosario central' not in c['nombre'].lower()
            ]
            
            if clubes_validos and jugador.get('partidos', 0) >= 5:
                jugador['clubes_validos'] = clubes_validos
                result.append(jugador)
        
        return result
    
    def _generar_lista_clubes(self, jugadores: List[Dict], posiciones: List[PosicionVacia], rng: random.Random) -> List[str]:
        """Generate ordered list of clubs to show (one per position)"""
        # Get all unique clubs
        todos_clubes = set()
        for jugador in jugadores:
            todos_clubes.update(jugador.get('clubes_validos', []))
        
        todos_clubes_list = list(todos_clubes)
        rng.shuffle(todos_clubes_list)
        
        # Need as many clubs as positions (11)
        clubes_orden = todos_clubes_list[:len(posiciones)]
        
        return clubes_orden
    
    def _elegir_formacion(self, rng: random.Random) -> Tuple[str, List[Dict]]:
        """
        Choose a formation that hasn't been used today
        
        Returns:
            Tuple of (formation_name, positions_list)
        """
        formaciones_disponibles = list(self.formaciones_data['formaciones'].keys())
        
        # Filter out formations already used today
        formaciones_no_usadas = [f for f in formaciones_disponibles if f not in self._formaciones_usadas_hoy]
        
        # If all have been used, reset
        if not formaciones_no_usadas:
            self._formaciones_usadas_hoy.clear()
            formaciones_no_usadas = formaciones_disponibles
        
        # Choose one
        formacion_elegida = rng.choice(formaciones_no_usadas)
        self._formaciones_usadas_hoy.add(formacion_elegida)
        
        # Get positions list
        posiciones_config = self.formaciones_data['formaciones'][formacion_elegida]['posiciones']
        
        return formacion_elegida, posiciones_config
    
    def _generate_equipo_del_dia(self, game_type: str, clubs_permitidos: Set[str]) -> EquipoDelDiaGame:
        """Generate Equipo del Día game with new mechanics"""
        seed = self._get_daily_seed(game_type)
        rng = random.Random(seed)
        game_id = self._get_game_id(game_type)
        
        # Get players who played in RC + permitted clubs
        jugadores = self._get_jugadores_con_clubes(clubs_permitidos)
        
        if len(jugadores) < 11:
            raise ValueError(f"No hay suficientes jugadores ({len(jugadores)}) para el juego")
        
        # Choose formation (ensuring no repetition within the day)
        formacion_nombre, posiciones_config = self._elegir_formacion(rng)
        
        # Create empty positions based on formation config
        posiciones = []
        for pos_def in posiciones_config:
            posicion = pos_def['posicion']
            cantidad = pos_def['cantidad']
            for _ in range(cantidad):
                posiciones.append(PosicionVacia(
                    posicion=posicion,
                    revelado=False
                ))
        
        # Generate club list (11 clubs, one per position)
        clubes_list = self._generar_lista_clubes(jugadores, posiciones, rng)
        
        # Select first club
        primer_club = clubes_list[0] if clubes_list else "River Plate"
        
        # Select a coach
        tecnicos_jugadores = self.data_loader.load_tecnicos_jugadores()
        tecnicos = list(tecnicos_jugadores.get('tecnicos', {}).keys())
        entrenador = rng.choice(tecnicos) if tecnicos else "Miguel Russo"
        
        # Store game state in cache
        self._games_cache[game_id] = {
            'clubes_list': clubes_list,
            'clubes_index': 0,
            'jugadores': jugadores,
            'formacion_nombre': formacion_nombre,
            'posiciones_config': posiciones_config,
            'posiciones': [p.model_dump() for p in posiciones],
            'entrenador': entrenador,
            'categoria': game_type.replace('equipo_', '')
        }
        
        return EquipoDelDiaGame(
            game_id=game_id,
            fecha=date.today().isoformat(),
            tipo=game_type,
            formacion=formacion_nombre,
            posiciones=posiciones,
            club_actual=ClubActual(
                nombre=primer_club,
                logo_url=self._get_logo_url(primer_club),
                pais=self._get_club_country(primer_club) or "Desconocido"
            ),
            entrenador_apellido=entrenador.split()[-1],
            entrenador_nombre_completo=entrenador,
            entrenador_revelado=False,
            jugadores_revelados=0,
            pistas_disponibles=3
        )
    
    def generate_equipo_nacional(self) -> EquipoDelDiaGame:
        """Generate Equipo Nacional del Día"""
        clubs_argentinos = self._get_all_clubs_by_category('Nacional')
        return self._generate_equipo_del_dia('equipo_nacional', clubs_argentinos)
    
    def generate_equipo_europeo(self) -> EquipoDelDiaGame:
        """Generate Equipo Europeo del Día"""
        clubs_europeos = self._get_all_clubs_by_category('Internacional')
        return self._generate_equipo_del_dia('equipo_europeo', clubs_europeos)
    
    def generate_equipo_latinoamericano(self) -> EquipoDelDiaGame:
        """Generate Equipo Latinoamericano del Día"""
        clubs_latinoamericanos = self._get_all_clubs_by_category('Latinoamérica')
        return self._generate_equipo_del_dia('equipo_latinoamericano', clubs_latinoamericanos)
    
    def verificar_respuesta(self, game_id: str, game_type: str, respuesta: str) -> Dict[str, Any]:
        """Verify player guess - NEW LOGIC"""
        # Normalize user input (remove accents, lowercase)
        respuesta_normalizada = self._normalize_text(respuesta.strip())
        
        # Get game state
        if game_id not in self._games_cache:
            # Regenerate game
            if 'nacional' in game_type:
                self.generate_equipo_nacional()
            elif 'europeo' in game_type:
                self.generate_equipo_europeo()
            elif 'latinoamericano' in game_type:
                self.generate_equipo_latinoamericano()
        
        game_state = self._games_cache.get(game_id)
        if not game_state:
            return {'correcto': False, 'mensaje': 'Juego no encontrado'}
        
        # Get current club
        club_index = game_state['clubes_index']
        club_actual = game_state['clubes_list'][club_index]
        
        # Check if it's a coach that managed the current club
        tecnicos_data = self.data_loader.load_tecnicos()
        tecnicos_dict = tecnicos_data.get('tecnicos', {})
        
        tecnico_encontrado = None
        for tecnico_nombre, tecnico_info in tecnicos_dict.items():
            # Normalize coach names
            tecnico_apellido = tecnico_nombre.split()[-1]
            tecnico_apellido_normalizado = self._normalize_text(tecnico_apellido)
            tecnico_nombre_completo_normalizado = self._normalize_text(tecnico_nombre)
            
            # Check if the user's answer matches this coach
            if (tecnico_apellido_normalizado == respuesta_normalizada or 
                tecnico_nombre_completo_normalizado == respuesta_normalizada):
                
                # Check if this coach managed the current club
                clubes_historia = tecnico_info.get('clubes_historia', [])
                for club_periodo in clubes_historia:
                    club_nombre = club_periodo.get('club', '')
                    if self._normalize_text(club_nombre) == self._normalize_text(club_actual):
                        tecnico_encontrado = tecnico_nombre
                        break
                
                if tecnico_encontrado:
                    break
        
        if tecnico_encontrado:
            # Get tecnico info for image
            tecnico_info = tecnicos_dict.get(tecnico_encontrado, {})
            
            return {
                'correcto': True,
                'mensaje': f'¡Correcto! DT: {tecnico_encontrado}',
                'jugador_revelado': {
                    'nombre': tecnico_encontrado,
                    'posicion': 'DT',
                    'tipo': 'entrenador',
                    'image_url': self._get_tecnico_image_url(tecnico_info)
                },
                'posicion_asignada': 'DT'
            }
        
        # Search for player
        jugadores = game_state['jugadores']
        jugador_encontrado = None
        
        for jugador in jugadores:
            # Use 'apellido' field if available, fallback to splitting nombre
            apellido_original = jugador.get('apellido', jugador['nombre'].split()[-1])
            apellido_normalizado = self._normalize_text(apellido_original)
            nombre_completo_normalizado = self._normalize_text(jugador['nombre'])
            
            # Match by apellido or full name (both normalized)
            if apellido_normalizado == respuesta_normalizada or nombre_completo_normalizado == respuesta_normalizada:
                # Check if played in current club
                clubes_jugador = jugador.get('clubes_validos', [])
                if club_actual in clubes_jugador:
                    jugador_encontrado = jugador
                    break
        
        if not jugador_encontrado:
            return {
                'correcto': False,
                'mensaje': f'El jugador no jugó en {club_actual} o no existe'
            }
        
        # Find available position for this player
        posiciones = game_state['posiciones']
        # Get all valid positions for this player (from posiciones list)
        posiciones_jugador = self._get_all_valid_positions(jugador_encontrado)
        
        posicion_asignada = None
        for i, pos in enumerate(posiciones):
            if not pos['revelado']:
                pos_type = pos['posicion']
                if pos_type in posiciones_jugador or (pos_type == 'DC' and 'DC_delantero' in posiciones_jugador):
                    # Assign to this position
                    pos['revelado'] = True
                    pos['jugador_nombre'] = jugador_encontrado['nombre']
                    # Use 'apellido' field if available, fallback to splitting nombre
                    pos['jugador_apellido'] = jugador_encontrado.get('apellido', jugador_encontrado['nombre'].split()[-1])
                    # Add image URL
                    pos['image_url'] = self._get_jugador_image_url(jugador_encontrado)
                    posicion_asignada = pos_type
                    break
        
        if not posicion_asignada:
            return {
                'correcto': False,
                'mensaje': f'{jugador_encontrado["nombre"]} no puede ocupar ninguna posición vacía'
            }
        
        # Move to next club
        game_state['clubes_index'] = min(club_index + 1, len(game_state['clubes_list']) - 1)
        next_club = game_state['clubes_list'][game_state['clubes_index']]
        
        return {
            'correcto': True,
            'mensaje': f'¡Correcto! {jugador_encontrado["nombre"]} - {posicion_asignada}',
            'jugador_revelado': {
                'nombre': jugador_encontrado['nombre'],
                'apellido': jugador_encontrado.get('apellido', jugador_encontrado['nombre'].split()[-1]),
                'posicion': posicion_asignada,
                'club': club_actual,
                'image_url': self._get_jugador_image_url(jugador_encontrado)
            },
            'posicion_asignada': posicion_asignada,
            'nuevo_club': {
                'nombre': next_club,
                'logo_url': self._get_logo_url(next_club),
                'pais': self._get_club_country(next_club) or "Desconocido"
            }
        }


# Singleton instance
game_generator_service = GameGeneratorService()
