"""
Service to generate daily games
"""
import random
from datetime import datetime, date
from typing import Dict, List, Any, Optional
from app.services.data_loader import data_loader_service
from app.schemas.game import (
    EquipoDelDiaGame,
    JugadorFormacion,
    OrbitaGame,
    ElementoOrbital
)


class GameGeneratorService:
    """Generates daily games with deterministic randomness based on date"""
    
    # Mapeo de posiciones de Transfermarkt a posiciones de formación
    POSICION_MAPPING = {
        # Porteros
        'portero': ['PO'],
        'arquero': ['PO'],
        'goalkeeper': ['PO'],
        
        # Defensas
        'defensa central': ['DC'],
        'defensa': ['DC', 'ED', 'EI'],
        'lateral derecho': ['ED'],
        'lateral izquierdo': ['EI'],
        'lateral': ['ED', 'EI'],
        'defensor': ['DC', 'ED', 'EI'],
        
        # Mediocampistas
        'mediocentro': ['MC'],
        'mediocampista': ['MC', 'MD', 'MI'],
        'pivote': ['MC'],
        'interior derecho': ['MD'],
        'interior izquierdo': ['MI'],
        'volante': ['MC', 'MD', 'MI'],
        'medio': ['MC', 'MD', 'MI'],
        
        # Delanteros
        'delantero': ['CT'],
        'delantero centro': ['CT'],
        'extremo': ['CT'],
        'atacante': ['CT'],
        'punta': ['CT']
    }
    
    def __init__(self):
        self.data_loader = data_loader_service
    
    def _get_daily_seed(self, game_type: str) -> int:
        """Generate seed based on current date and game type"""
        today = date.today()
        type_offset = hash(game_type) % 1000
        return int(today.strftime("%Y%m%d")) + type_offset
    
    def _get_game_id(self, game_type: str) -> str:
        """Generate unique game ID for today"""
        today = date.today()
        return f"{game_type}_{today.strftime('%Y%m%d')}"
    
    def _get_posiciones_posibles(self, posicion_jugador: str) -> List[str]:
        """Get possible formation positions for a player position"""
        posicion_lower = posicion_jugador.lower()
        
        for key, positions in self.POSICION_MAPPING.items():
            if key in posicion_lower:
                return positions
        
        # Default por tipo general
        if 'porter' in posicion_lower or 'arquer' in posicion_lower:
            return ['PO']
        elif 'defens' in posicion_lower or 'lateral' in posicion_lower:
            return ['DC', 'ED', 'EI']
        elif 'medio' in posicion_lower or 'volante' in posicion_lower:
            return ['MC', 'MD', 'MI']
        elif 'delant' in posicion_lower or 'atac' in posicion_lower:
            return ['CT']
        
        return ['MC']  # Default
    
    def _crear_formacion(self, jugadores: List[Dict], tipo: str = "nacional") -> List[JugadorFormacion]:
        """Create formation with players in positions"""
        # Formación simplificada: 1 PO, 3 defensas, 4 medios, 3 delanteros
        # Ser más flexible con las posiciones específicas
        posiciones_objetivo = [
            ('PO', 1),      # Portero
            ('DC', 3),      # 3 defensas (cualquier tipo)
            ('MC', 4),      # 4 mediocampistas (cualquier tipo)
            ('CT', 3)       # 3 delanteros
        ]
        
        formacion = []
        jugadores_asignados = set()
        
        # Organizar jugadores por línea general (más flexible)
        jugadores_por_linea = {
            'PO': [],
            'DC': [],  # Todos los defensas
            'MC': [],  # Todos los mediocampistas
            'CT': []   # Todos los delanteros
        }
        
        for jug in jugadores:
            if 'posicion' not in jug:
                continue
            posiciones_posibles = self._get_posiciones_posibles(jug['posicion'])
            # Agrupar por línea principal
            for pos in posiciones_posibles:
                if pos == 'PO':
                    jugadores_por_linea['PO'].append(jug)
                elif pos in ['DC', 'ED', 'EI']:
                    if jug not in jugadores_por_linea['DC']:
                        jugadores_por_linea['DC'].append(jug)
                elif pos in ['MC', 'MD', 'MI']:
                    if jug not in jugadores_por_linea['MC']:
                        jugadores_por_linea['MC'].append(jug)
                elif pos == 'CT':
                    if jug not in jugadores_por_linea['CT']:
                        jugadores_por_linea['CT'].append(jug)
        
        # Asignar jugadores a posiciones
        posiciones_usadas = {'PO': 0, 'DC': 0, 'ED': 0, 'EI': 0, 'MC': 0, 'MD': 0, 'MI': 0, 'CT': 0}
        
        for linea, cantidad in posiciones_objetivo:
            candidatos = [j for j in jugadores_por_linea.get(linea, []) if j['nombre'] not in jugadores_asignados]
            
            for i in range(cantidad):
                if candidatos:
                    jugador = random.choice(candidatos)
                    candidatos.remove(jugador)
                    jugadores_asignados.add(jugador['nombre'])
                    
                    # Asignar posición específica basada en la línea
                    if linea == 'DC':
                        if posiciones_usadas['DC'] < 1:
                            pos_especifica = 'DC'
                            posiciones_usadas['DC'] += 1
                        elif posiciones_usadas['ED'] < 1:
                            pos_especifica = 'ED'
                            posiciones_usadas['ED'] += 1
                        else:
                            pos_especifica = 'EI'
                            posiciones_usadas['EI'] += 1
                    elif linea == 'MC':
                        if posiciones_usadas['MC'] < 2:
                            pos_especifica = 'MC'
                            posiciones_usadas['MC'] += 1
                        elif posiciones_usadas['MD'] < 1:
                            pos_especifica = 'MD'
                            posiciones_usadas['MD'] += 1
                        else:
                            pos_especifica = 'MI'
                            posiciones_usadas['MI'] += 1
                    else:
                        pos_especifica = linea
                    
                    # Extraer apellido
                    nombre_completo = jugador['nombre']
                    partes = nombre_completo.split()
                    apellido = partes[-1] if partes else nombre_completo
                    
                    jugador_formacion = JugadorFormacion(
                        posicion=pos_especifica,
                        nombre=nombre_completo,
                        apellido=apellido,
                        nombre_completo=nombre_completo,
                        image_url=f"/api/v1/static/jugadores/{self._sanitize_filename(nombre_completo)}.jpg",
                        revelado=False,
                        nacionalidad=jugador.get('nacionalidad'),
                        partidos=jugador.get('partidos', jugador.get('apariciones', 0))
                    )
                    formacion.append(jugador_formacion)
        
        return formacion
    
    def generate_equipo_nacional(self) -> EquipoDelDiaGame:
        """Generate Equipo Nacional del Día"""
        game_type = "equipo_nacional"
        seed = self._get_daily_seed(game_type)
        random.seed(seed)
        
        # Obtener técnicos que dirigieron en Argentina
        tecnicos_data = self.data_loader.load_tecnicos_jugadores()
        if not tecnicos_data or 'tecnicos' not in tecnicos_data:
            raise ValueError("No hay datos de técnicos disponibles")
        
        tecnicos = tecnicos_data['tecnicos']
        
        # Filtrar técnicos con suficientes jugadores argentinos
        tecnicos_validos = []
        for tecnico_nombre, data in tecnicos.items():
            torneos = data.get('torneos', [])
            # Buscar torneos con suficientes jugadores argentinos
            for torneo_data in torneos:
                jugadores = torneo_data.get('jugadores', [])
                # Filtrar solo jugadores argentinos
                jugadores_argentinos = [j for j in jugadores if j.get('nacionalidad', '') == 'Argentina']
                
                if len(jugadores_argentinos) >= 11:
                    tecnicos_validos.append({
                        'nombre': tecnico_nombre,
                        'torneo': f"{torneo_data.get('torneo', 'Torneo')} {torneo_data.get('temporada', '')}",
                        'jugadores': jugadores_argentinos
                    })
        
        if not tecnicos_validos:
            raise ValueError("No hay técnicos con suficientes jugadores argentinos")
        
        # Seleccionar técnico y torneo aleatorio
        seleccion = random.choice(tecnicos_validos)
        
        # Crear formación
        formacion = self._crear_formacion(seleccion['jugadores'], tipo="nacional")
        
        if len(formacion) < 9:
            raise ValueError(f"No se pudo completar la formación (solo {len(formacion)} jugadores)")
        
        return EquipoDelDiaGame(
            game_id=self._get_game_id(game_type),
            fecha=date.today().strftime("%Y-%m-%d"),
            tipo=game_type,
            formacion="3-4-3",
            jugadores=formacion,
            pistas_disponibles=3,
            dt_nombre=seleccion['nombre'],
            competencia=seleccion['torneo']
        )
    
    def generate_equipo_internacional(self) -> EquipoDelDiaGame:
        """Generate Equipo Internacional del Día"""
        game_type = "equipo_internacional"
        seed = self._get_daily_seed(game_type)
        random.seed(seed)
        
        # Similar a nacional pero filtrando jugadores internacionales
        tecnicos_data = self.data_loader.load_tecnicos_jugadores()
        if not tecnicos_data or 'tecnicos' not in tecnicos_data:
            raise ValueError("No hay datos de técnicos disponibles")
        
        tecnicos = tecnicos_data['tecnicos']
        
        tecnicos_validos = []
        for tecnico_nombre, data in tecnicos.items():
            torneos = data.get('torneos', [])
            for torneo_data in torneos:
                jugadores = torneo_data.get('jugadores', [])
                
                # Filtrar solo jugadores NO argentinos
                jugadores_internacionales = [j for j in jugadores if j.get('nacionalidad', '') != 'Argentina']
                
                if len(jugadores_internacionales) >= 11:
                    tecnicos_validos.append({
                        'nombre': tecnico_nombre,
                        'torneo': f"{torneo_data.get('torneo', 'Torneo')} {torneo_data.get('temporada', '')}",
                        'jugadores': jugadores_internacionales
                    })
        
        if not tecnicos_validos:
            raise ValueError("No hay suficientes jugadores internacionales")
        
        seleccion = random.choice(tecnicos_validos)
        formacion = self._crear_formacion(seleccion['jugadores'], tipo="internacional")
        
        if len(formacion) < 9:
            raise ValueError(f"No se pudo completar la formación internacional (solo {len(formacion)} jugadores)")
        
        return EquipoDelDiaGame(
            game_id=self._get_game_id(game_type),
            fecha=date.today().strftime("%Y-%m-%d"),
            tipo=game_type,
            formacion="3-4-3",
            jugadores=formacion,
            pistas_disponibles=3,
            dt_nombre=seleccion['nombre'],
            competencia=seleccion['torneo']
        )
    
    def generate_orbita_del_dia(self) -> OrbitaGame:
        """Generate Órbita del Día"""
        game_type = "orbita"
        seed = self._get_daily_seed(game_type)
        random.seed(seed)
        
        # Get coaches with players data
        tecnicos_data = self.data_loader.load_tecnicos_jugadores()
        if not tecnicos_data or 'tecnicos' not in tecnicos_data:
            raise ValueError("No hay técnicos disponibles para Órbita")
        
        tecnicos = tecnicos_data['tecnicos']
        
        # Get coach info
        all_tecnicos = self.data_loader.get_all_tecnicos()
        
        # Select random coach with enough data
        tecnicos_validos = []
        for tecnico_nombre, data in tecnicos.items():
            torneos = data.get('torneos', [])
            if torneos and len(torneos) > 0:
                tecnicos_validos.append(tecnico_nombre)
        
        if not tecnicos_validos:
            raise ValueError("No hay técnicos con torneos disponibles")
        
        tecnico_nombre = random.choice(tecnicos_validos)
        tecnico_jugadores_data = tecnicos[tecnico_nombre]
        tecnico_info = all_tecnicos.get(tecnico_nombre, {})
        
        # Choose game mode randomly
        modos = ["mas_minutos", "mas_goles", "mas_apariciones"]
        modo = random.choice(modos)
        
        # Get available tournaments
        torneos = tecnico_jugadores_data.get('torneos', [])
        
        # Select a tournament with enough players
        torneos_validos = [t for t in torneos if len(t.get('jugadores', [])) >= 6]
        
        if not torneos_validos:
            torneos_validos = torneos
        
        if not torneos_validos:
            raise ValueError(f"No hay torneos válidos para {tecnico_nombre}")
        
        torneo_seleccionado = random.choice(torneos_validos)
        jugadores_competencia = torneo_seleccionado.get('jugadores', [])
        
        # Sort players based on mode
        if modo == "mas_minutos":
            jugadores_sorted = sorted(
                jugadores_competencia,
                key=lambda x: x.get("minutos", 0),
                reverse=True
            )
        elif modo == "mas_goles":
            jugadores_sorted = sorted(
                jugadores_competencia,
                key=lambda x: x.get("goles", 0),
                reverse=True
            )
        else:  # mas_apariciones
            jugadores_sorted = sorted(
                jugadores_competencia,
                key=lambda x: x.get("apariciones", 0),
                reverse=True
            )
        
        # Select top 8-12 players as orbital elements
        num_elementos = min(random.randint(8, 12), len(jugadores_sorted))
        jugadores_seleccionados = jugadores_sorted[:num_elementos]
        
        # Create orbital elements
        elementos_orbitales = []
        for idx, jug in enumerate(jugadores_seleccionados):
            elemento = ElementoOrbital(
                id=f"orbital_{idx}",
                tipo="jugador",
                nombre=jug.get("nombre", "???"),
                image_url=f"/api/v1/static/jugadores/{self._sanitize_filename(jug.get('nombre', ''))}.jpg",
                revelado=False
            )
            elementos_orbitales.append(elemento)
        
        # Protagonista (coach)
        protagonista = {
            "nombre": tecnico_nombre,
            "image_url": f"/api/v1/static/tecnicos/{self._sanitize_filename(tecnico_nombre)}.jpg",
            "nacionalidad": tecnico_info.get("nacionalidad", ""),
            "partidos_dirigidos": tecnico_info.get("partidos_dirigidos", 0)
        }
        
        competencia_nombre = f"{torneo_seleccionado.get('torneo', 'Torneo')} {torneo_seleccionado.get('temporada', '')}"
        
        return OrbitaGame(
            game_id=self._get_game_id(game_type),
            fecha=date.today().strftime("%Y-%m-%d"),
            tipo=game_type,
            protagonista=protagonista,
            elementos_orbitales=elementos_orbitales,
            modo_juego=modo,
            competencia=competencia_nombre,
            tiempo_limite=120
        )
    
    def _sanitize_filename(self, name: str) -> str:
        """Sanitize name for filename"""
        import re
        name = name.lower()
        name = re.sub(r'[áàäâ]', 'a', name)
        name = re.sub(r'[éèëê]', 'e', name)
        name = re.sub(r'[íìïî]', 'i', name)
        name = re.sub(r'[óòöô]', 'o', name)
        name = re.sub(r'[úùüû]', 'u', name)
        name = re.sub(r'[ñ]', 'n', name)
        name = re.sub(r'[^a-z0-9\s_-]', '', name)
        name = re.sub(r'\s+', '_', name)
        return name


# Singleton instance
game_generator_service = GameGeneratorService()
