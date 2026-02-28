"""
Pydantic schemas for game responses
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class ClubHistoria(BaseModel):
    """Club history item"""
    nombre: str
    pais: str
    periodo: str
    logo_url: Optional[str] = None


class EstadisticaTorneo(BaseModel):
    """Tournament statistics"""
    temporada: str
    competicion: str
    partidos: int = 0
    goles: int = 0
    minutos: int = 0
    amarillas: int = 0
    doble_amarillas: int = 0
    rojas: int = 0


class ElementoOrbital(BaseModel):
    """Orbital element for Orbita game"""
    id: str
    tipo: str  # "jugador", "estadistica"
    nombre: str = "???"
    valor: Optional[str] = None  # For statistics
    image_url: Optional[str] = None
    revelado: bool = False


class JugadorFormacion(BaseModel):
    """Player in formation"""
    posicion: str  # PO, DC, ED, EI, etc.
    nombre: str
    apellido: str
    nombre_completo: str
    image_url: Optional[str] = None
    revelado: bool = False
    nacionalidad: Optional[str] = None
    partidos: Optional[int] = None


class EquipoDelDiaGame(BaseModel):
    """Equipo del Día game data"""
    game_id: str
    fecha: str
    tipo: str  # "equipo_nacional" o "equipo_internacional"
    formacion: str = "3-4-3"  # Formación táctica
    jugadores: List[JugadorFormacion]  # 11 jugadores
    pistas_disponibles: int = 3
    dt_nombre: Optional[str] = None  # Director técnico (opcional)
    temporada: Optional[str] = None  # Ej: "2021"
    competencia: Optional[str] = None  # Ej: "Liga Profesional"


class OrbitaGame(BaseModel):
    """Órbita del Día game data"""
    game_id: str
    fecha: str
    tipo: str = "orbita"
    protagonista: Dict[str, Any]  # Técnico principal
    elementos_orbitales: List[ElementoOrbital]  # Jugadores/estadísticas
    modo_juego: str  # "mas_minutos", "mas_goles", "mas_apariciones"
    competencia: str  # "Liga Profesional", "Copa Libertadores", etc.
    tiempo_limite: int = 120  # seconds


class GameResponse(BaseModel):
    """Generic game response"""
    success: bool
    game_type: str
    game_id: str
    fecha: str
    data: Dict[str, Any]
    mensaje: Optional[str] = None


class GameGuess(BaseModel):
    """Player guess submission"""
    game_id: str
    game_type: str
    respuesta: str
    tiempo_jugado: Optional[int] = None  # seconds


class GameResult(BaseModel):
    """Result of a guess"""
    correcto: bool
    mensaje: str
    jugador_revelado: Optional[Dict[str, Any]] = None
    elementos_revelados: Optional[List[str]] = None
    pista_nueva: Optional[str] = None
    game_over: bool = False
    victoria: bool = False
