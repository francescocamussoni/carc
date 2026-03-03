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
        Keeps dots, spaces, and other punctuation to maintain club name consistency
        
        Examples:
            'Ángel Di María' -> 'angel di maria'
            'Pérez' -> 'perez'
            'Ind. Rivadavia' -> 'ind. rivadavia'
            'Def. y Justicia' -> 'def. y justicia'
        """
        if not text:
            return ""
        # Convert to NFD (decomposed) form, then remove combining characters (accents)
        nfd = unicodedata.normalize('NFD', text)
        without_accents = ''.join(char for char in nfd if unicodedata.category(char) != 'Mn')
        # Convert to lowercase and normalize whitespace
        cleaned = without_accents.lower()
        cleaned = ' '.join(cleaned.split())
        return cleaned
    
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
                return ['MO', 'MC']
            if 'derech' in pos_lower:
                return ['MD', 'MC']
            elif 'izquier' in pos_lower:
                return ['MI', 'MC']
            return ['MC']
        elif 'delant' in pos_lower or 'atac' in pos_lower:
            return ['DEL']
        
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
        
        # ✅ NUEVO: Default to Argentina if country not found (for Rosario Central and other Argentine clubs)
        if not pais:
            pais = "Argentina"
        
        # Normalize club name for filename (same logic as scraper in text_utils.py)
        import unicodedata
        import re
        
        filename = club_nombre.lower()
        # Remove accents
        nfd = unicodedata.normalize('NFD', filename)
        filename = ''.join(char for char in nfd if unicodedata.category(char) != 'Mn')
        # Replace ALL special characters (not just some) with underscore
        # This matches the scraper's logic: re.sub(r'[^a-z0-9]+', '_', nombre_limpio)
        # Examples: "Newell's" -> "newell_s", "O'Higgins" -> "o_higgins", "San Martín (T)" -> "san_martin_t"
        filename = re.sub(r'[^a-z0-9]+', '_', filename)
        # Remove trailing underscores
        filename = filename.strip('_')
        
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
            
            # Get clubs that are in the permitted list (normalize for comparison)
            clubes_validos = []
            for c in clubes_historia:
                club_nombre = c['nombre']
                # Skip Rosario Central
                if 'rosario central' in club_nombre.lower():
                    continue
                
                # Check if this club matches any in the permitted list (normalized)
                club_normalizado = self._normalize_text(club_nombre)
                for club_permitido in clubs_permitidos:
                    club_permitido_normalizado = self._normalize_text(club_permitido)
                    if club_normalizado == club_permitido_normalizado:
                        clubes_validos.append(club_nombre)
                        break
            
            if clubes_validos and jugador.get('partidos', 0) >= 1:
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
            # 'jugadores': jugadores,  # ❌ REMOVED: No longer needed - we search all players now
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
            # Verificar si el técnico ya fue revelado
            if game_state.get('entrenador_revelado', False):
                return {
                    'correcto': False,
                    'mensaje': 'El técnico ya fue adivinado'
                }
            
            # Get tecnico info for image
            tecnico_info = tecnicos_dict.get(tecnico_encontrado, {})
            
            # Marcar técnico como revelado
            game_state['entrenador_revelado'] = True
            
            # ✅ Cambiar al siguiente club (igual que con jugadores)
            club_index = game_state['clubes_index']
            game_state['clubes_index'] = min(club_index + 1, len(game_state['clubes_list']) - 1)
            next_club = game_state['clubes_list'][game_state['clubes_index']]
            
            # ✅ Verificar si el juego terminó (11 jugadores + 1 técnico = 12 personas)
            posiciones = game_state['posiciones']
            jugadores_revelados = sum(1 for p in posiciones if p.get('revelado', False))
            entrenador_revelado = game_state.get('entrenador_revelado', False)
            
            # Victoria si 11 jugadores + técnico revelados
            game_over = (jugadores_revelados >= 11 and entrenador_revelado)
            victoria = game_over
            
            mensaje = f'¡Correcto! DT: {tecnico_encontrado}'
            if victoria:
                mensaje = f'🎉 ¡Felicitaciones! Completaste el equipo. DT: {tecnico_encontrado}'
            
            return {
                'correcto': True,
                'mensaje': mensaje,
                'jugador_revelado': {
                    'nombre': tecnico_encontrado,
                    'posicion': 'DT',
                    'tipo': 'entrenador',
                    'image_url': self._get_tecnico_image_url(tecnico_info)
                },
                'posicion_asignada': 'DT',
                'nuevo_club': {
                    'nombre': next_club,
                    'logo_url': self._get_logo_url(next_club),
                    'pais': self._get_club_country(next_club) or "Desconocido"
                },
                'game_over': game_over,
                'victoria': victoria
            }
        
        # Search for ALL players matching the input
        # 🔧 FIX: Search in ALL players, not just game_state players
        # This allows any player who played in RC + current club to be valid
        all_jugadores = self.data_loader.get_all_jugadores()
        jugadores_encontrados = []
        
        for jugador in all_jugadores:
            # Use 'apellido' field if available, fallback to splitting nombre
            apellido_original = jugador.get('apellido', jugador['nombre'].split()[-1])
            apellido_normalizado = self._normalize_text(apellido_original)
            nombre_completo_normalizado = self._normalize_text(jugador['nombre'])
            
            # Match by apellido or full name (both normalized)
            if apellido_normalizado == respuesta_normalizada or nombre_completo_normalizado == respuesta_normalizada:
                # 🔧 FIX: Check if played in Rosario Central first
                clubes_historia = jugador.get('clubes_historia', [])
                tiene_rc = any('rosario central' in c.get('nombre', '').lower() for c in clubes_historia)
                
                if not tiene_rc:
                    continue
                
                # Check if played in current club (normalize club names for comparison)
                club_actual_normalizado = self._normalize_text(club_actual)
                
                # Check if any of the player's clubs matches the current club
                for club_hist in clubes_historia:
                    club_nombre = club_hist.get('nombre', '')
                    club_normalizado = self._normalize_text(club_nombre)
                    if club_actual_normalizado == club_normalizado:
                        jugadores_encontrados.append(jugador)
                        break  # ✅ Break ONLY if we found a match
        
        if not jugadores_encontrados:
            return {
                'correcto': False,
                'mensaje': f'El jugador no jugó en {club_actual} o no existe'
            }
        
        # ✅ NUEVO: Si hay múltiples jugadores con el mismo apellido, filtrar por posiciones disponibles
        posiciones = game_state['posiciones']
        jugadores_con_posiciones = []
        
        for jugador in jugadores_encontrados:
            posiciones_jugador = self._get_all_valid_positions(jugador)
            # Check if this player can occupy any available position
            puede_jugar = False
            for pos in posiciones:
                if not pos['revelado'] and pos['posicion'] in posiciones_jugador:
                    puede_jugar = True
                    break
            
            if puede_jugar:
                jugadores_con_posiciones.append(jugador)
        
        if not jugadores_con_posiciones:
            return {
                'correcto': False,
                'mensaje': f'Ningún jugador con ese apellido puede ocupar las posiciones vacías'
            }
        
        # ✅ NUEVO: Si hay múltiples jugadores válidos, pedir selección
        if len(jugadores_con_posiciones) > 1:
            game_state['pending_player_selection'] = {
                'jugadores': jugadores_con_posiciones,
                'apellido': respuesta.strip()
            }
            
            opciones = [f"{j['nombre']}" for j in jugadores_con_posiciones]
            
            return {
                'correcto': True,
                'requiere_seleccion_jugador': True,
                'mensaje': f'Hay {len(jugadores_con_posiciones)} jugadores con ese apellido. Elegí uno:',
                'jugadores_disponibles': opciones
            }
        
        # Solo hay un jugador válido
        jugador_encontrado = jugadores_con_posiciones[0]
        
        # Find available positions for this player
        posiciones = game_state['posiciones']
        # Get all valid positions for this player (from posiciones list)
        posiciones_jugador = self._get_all_valid_positions(jugador_encontrado)
        
        # Find ALL available positions that this player can occupy
        posiciones_disponibles = []
        for i, pos in enumerate(posiciones):
            if not pos['revelado']:
                pos_type = pos['posicion']
                if pos_type in posiciones_jugador:
                    posiciones_disponibles.append({
                        'posicion': pos_type,
                        'index': i
                    })
        
        if not posiciones_disponibles:
            return {
                'correcto': False,
                'mensaje': f'{jugador_encontrado["nombre"]} no puede ocupar ninguna posición vacía'
            }
        
        # Get unique position types available
        posiciones_unicas = list(set(p['posicion'] for p in posiciones_disponibles))
        
        # If multiple position TYPES available, ask user to choose
        if len(posiciones_unicas) > 1:
            # Store pending player in game state
            game_state['pending_player'] = {
                'jugador': jugador_encontrado,
                'posiciones_disponibles': posiciones_disponibles
            }
            
            return {
                'correcto': True,
                'requiere_seleccion': True,
                'mensaje': f'¡Correcto! {jugador_encontrado["nombre"]} puede jugar en varias posiciones. Elegí una:',
                'jugador_revelado': {
                    'nombre': jugador_encontrado['nombre'],
                    'apellido': jugador_encontrado.get('apellido', jugador_encontrado['nombre'].split()[-1]),
                    'image_url': self._get_jugador_image_url(jugador_encontrado)
                },
                'posiciones_disponibles': sorted(posiciones_unicas)  # Unique positions only, sorted
            }
        
        # Only one position available, assign automatically
        posicion_elegida = posiciones_disponibles[0]
        posicion_asignada = posicion_elegida['posicion']
        pos_index = posicion_elegida['index']
        
        # Assign to position
        posiciones[pos_index]['revelado'] = True
        posiciones[pos_index]['jugador_nombre'] = jugador_encontrado['nombre']
        posiciones[pos_index]['jugador_apellido'] = jugador_encontrado.get('apellido', jugador_encontrado['nombre'].split()[-1])
        posiciones[pos_index]['image_url'] = self._get_jugador_image_url(jugador_encontrado)
        
        # Move to next club
        game_state['clubes_index'] = min(club_index + 1, len(game_state['clubes_list']) - 1)
        next_club = game_state['clubes_list'][game_state['clubes_index']]
        
        # ✅ Verificar victoria: 11 jugadores + 1 técnico = 12 personas
        jugadores_revelados = sum(1 for p in posiciones if p.get('revelado', False))
        entrenador_revelado = game_state.get('entrenador_revelado', False)
        game_over = (jugadores_revelados >= 11 and entrenador_revelado)
        victoria = game_over
        
        mensaje = f'¡Correcto! {jugador_encontrado["nombre"]} - {posicion_asignada}'
        if victoria:
            mensaje = f'🎉 ¡Felicitaciones! Completaste el equipo con {jugador_encontrado["nombre"]}'
        
        return {
            'correcto': True,
            'mensaje': mensaje,
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
            },
            'game_over': game_over,
            'victoria': victoria
        }
    
    def confirmar_posicion(self, game_id: str, posicion_elegida: str) -> Dict[str, Any]:
        """Confirm the position chosen by the user for a multi-position player"""
        game_state = self._games_cache.get(game_id)
        if not game_state:
            return {'correcto': False, 'mensaje': 'Juego no encontrado'}
        
        # Get pending player
        pending_data = game_state.get('pending_player')
        if not pending_data:
            return {'correcto': False, 'mensaje': 'No hay jugador pendiente de asignación'}
        
        jugador_encontrado = pending_data['jugador']
        posiciones_disponibles = pending_data['posiciones_disponibles']
        
        # Find the FIRST available position of the chosen type
        posicion_data = None
        for p in posiciones_disponibles:
            if p['posicion'] == posicion_elegida:
                posicion_data = p
                break  # Take the first one of this type
        
        if not posicion_data:
            return {'correcto': False, 'mensaje': 'Posición no válida'}
        
        # Assign player to the first available position of chosen type
        posiciones = game_state['posiciones']
        pos_index = posicion_data['index']
        posiciones[pos_index]['revelado'] = True
        posiciones[pos_index]['jugador_nombre'] = jugador_encontrado['nombre']
        posiciones[pos_index]['jugador_apellido'] = jugador_encontrado.get('apellido', jugador_encontrado['nombre'].split()[-1])
        posiciones[pos_index]['image_url'] = self._get_jugador_image_url(jugador_encontrado)
        
        # Get current club
        club_index = game_state['clubes_index']
        club_actual = game_state['clubes_list'][club_index]
        
        # Move to next club
        game_state['clubes_index'] = min(club_index + 1, len(game_state['clubes_list']) - 1)
        next_club = game_state['clubes_list'][game_state['clubes_index']]
        
        # ✅ Verificar victoria: 11 jugadores + 1 técnico = 12 personas
        jugadores_revelados = sum(1 for p in posiciones if p.get('revelado', False))
        entrenador_revelado = game_state.get('entrenador_revelado', False)
        game_over = (jugadores_revelados >= 11 and entrenador_revelado)
        victoria = game_over
        
        mensaje = f'¡Correcto! {jugador_encontrado["nombre"]} - {posicion_elegida}'
        if victoria:
            mensaje = f'🎉 ¡Felicitaciones! Completaste el equipo con {jugador_encontrado["nombre"]}'
        
        # Clear pending player
        del game_state['pending_player']
        
        return {
            'correcto': True,
            'mensaje': mensaje,
            'jugador_revelado': {
                'nombre': jugador_encontrado['nombre'],
                'apellido': jugador_encontrado.get('apellido', jugador_encontrado['nombre'].split()[-1]),
                'posicion': posicion_elegida,
                'club': club_actual,
                'image_url': self._get_jugador_image_url(jugador_encontrado)
            },
            'posicion_asignada': posicion_elegida,
            'nuevo_club': {
                'nombre': next_club,
                'logo_url': self._get_logo_url(next_club),
                'pais': self._get_club_country(next_club) or "Desconocido"
            },
            'game_over': game_over,
            'victoria': victoria
        }
    
    def confirmar_jugador(self, game_id: str, nombre_jugador: str) -> Dict[str, Any]:
        """Confirm the player chosen by the user when multiple players match"""
        game_state = self._games_cache.get(game_id)
        if not game_state:
            return {'correcto': False, 'mensaje': 'Juego no encontrado'}
        
        # Get pending player selection
        pending_data = game_state.get('pending_player_selection')
        if not pending_data:
            return {'correcto': False, 'mensaje': 'No hay selección de jugador pendiente'}
        
        jugadores_disponibles = pending_data['jugadores']
        
        # Find the selected player
        jugador_encontrado = None
        for jugador in jugadores_disponibles:
            if jugador['nombre'] == nombre_jugador:
                jugador_encontrado = jugador
                break
        
        if not jugador_encontrado:
            return {'correcto': False, 'mensaje': 'Jugador no válido'}
        
        # Clear pending selection
        del game_state['pending_player_selection']
        
        # Now continue with normal flow: find positions for this player
        posiciones = game_state['posiciones']
        posiciones_jugador = self._get_all_valid_positions(jugador_encontrado)
        
        # Find ALL available positions that this player can occupy
        posiciones_disponibles = []
        for i, pos in enumerate(posiciones):
            if not pos['revelado']:
                pos_type = pos['posicion']
                if pos_type in posiciones_jugador:
                    posiciones_disponibles.append({
                        'posicion': pos_type,
                        'index': i
                    })
        
        if not posiciones_disponibles:
            return {
                'correcto': False,
                'mensaje': f'{jugador_encontrado["nombre"]} no puede ocupar ninguna posición vacía'
            }
        
        # Get unique position types available
        posiciones_unicas = list(set(p['posicion'] for p in posiciones_disponibles))
        
        # If multiple position TYPES available, ask user to choose
        if len(posiciones_unicas) > 1:
            game_state['pending_player'] = {
                'jugador': jugador_encontrado,
                'posiciones_disponibles': posiciones_disponibles
            }
            
            return {
                'correcto': True,
                'requiere_seleccion': True,
                'mensaje': f'¡Correcto! {jugador_encontrado["nombre"]} puede jugar en varias posiciones. Elegí una:',
                'jugador_revelado': {
                    'nombre': jugador_encontrado['nombre'],
                    'apellido': jugador_encontrado.get('apellido', jugador_encontrado['nombre'].split()[-1]),
                    'image_url': self._get_jugador_image_url(jugador_encontrado)
                },
                'posiciones_disponibles': sorted(posiciones_unicas)
            }
        
        # Only one position available, assign automatically
        club_index = game_state['clubes_index']
        club_actual = game_state['clubes_list'][club_index]
        
        posicion_elegida = posiciones_disponibles[0]
        posicion_asignada = posicion_elegida['posicion']
        pos_index = posicion_elegida['index']
        
        # Assign to position
        posiciones[pos_index]['revelado'] = True
        posiciones[pos_index]['jugador_nombre'] = jugador_encontrado['nombre']
        posiciones[pos_index]['jugador_apellido'] = jugador_encontrado.get('apellido', jugador_encontrado['nombre'].split()[-1])
        posiciones[pos_index]['image_url'] = self._get_jugador_image_url(jugador_encontrado)
        
        # Move to next club
        game_state['clubes_index'] = min(club_index + 1, len(game_state['clubes_list']) - 1)
        next_club = game_state['clubes_list'][game_state['clubes_index']]
        
        # Verificar victoria: 11 jugadores + 1 técnico = 12 personas
        jugadores_revelados = sum(1 for p in posiciones if p.get('revelado', False))
        entrenador_revelado = game_state.get('entrenador_revelado', False)
        game_over = (jugadores_revelados >= 11 and entrenador_revelado)
        victoria = game_over
        
        mensaje = f'¡Correcto! {jugador_encontrado["nombre"]} - {posicion_asignada}'
        if victoria:
            mensaje = f'🎉 ¡Felicitaciones! Completaste el equipo con {jugador_encontrado["nombre"]}'
        
        return {
            'correcto': True,
            'mensaje': mensaje,
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
            },
            'game_over': game_over,
            'victoria': victoria
        }
    
    def obtener_pista(self, game_id: str) -> Dict[str, Any]:
        """
        Get hints for the current club using optimized index (O(1) lookup)
        
        Returns hints:
        - Primera letra del apellido  
        - Posición principal del jugador
        - Otro club donde jugó (si hay alguno disponible)
        """
        game_state = self._games_cache.get(game_id)
        if not game_state:
            return {'error': 'Juego no encontrado'}
        
        # Get current club
        club_index = game_state['clubes_index']
        club_actual = game_state['clubes_list'][club_index]
        posiciones = game_state['posiciones']
        
        # Find first available position
        posicion_disponible = None
        for pos in posiciones:
            if not pos['revelado']:
                posicion_disponible = pos['posicion']
                break
        
        if not posicion_disponible:
            return {'error': 'No hay posiciones disponibles'}
        
        # Get players for this club and position using optimized index (O(1))
        jugadores_posibles = self.data_loader.get_jugadores_por_club_posicion(
            club_actual,
            posicion_disponible
        )
        
        if not jugadores_posibles:
            # Fallback: try getting any player for this club
            jugadores_posibles = self.data_loader.get_jugadores_por_club_posicion(
                club_actual
            )
            
            if not jugadores_posibles:
                return {'error': 'No se encontró jugador válido para generar pista'}
        
        # Take first player
        jugador_sugerido = jugadores_posibles[0]
        
        # Generate hints
        apellido = jugador_sugerido.get('apellido', 'Desconocido')
        primera_letra = apellido[0].upper() if apellido else '?'
        
        # Main position
        posiciones_jugador = jugador_sugerido.get('posiciones', [])
        posicion_principal = posiciones_jugador[0] if posiciones_jugador else 'Desconocida'
        
        # Find another club (not RC, not current club)
        otros_clubes = jugador_sugerido.get('otros_clubes', [])
        otro_club = otros_clubes[0] if otros_clubes else None
        
        return {
            'pistas': {
                'letra_inicial': primera_letra,
                'posicion': posicion_principal,
                'otro_club': otro_club
            },
            'club_actual': club_actual
        }


# Singleton instance
game_generator_service = GameGeneratorService()
