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


class PosicionVacia(BaseModel):
    """Empty position in formation"""
    posicion: str  # PO, DC, ED, EI, MC, MD, MI, etc.
    revelado: bool = False
    jugador_nombre: Optional[str] = None
    jugador_apellido: Optional[str] = None


class ClubActual(BaseModel):
    """Current club to guess"""
    nombre: str
    logo_url: Optional[str] = None
    pais: str


class EquipoDelDiaGame(BaseModel):
    """Equipo del Día game data - Nueva mecánica"""
    game_id: str
    fecha: str
    tipo: str  # "equipo_nacional", "equipo_europeo", "equipo_latinoamericano"
    formacion: str  # "4-4-2" o "4-3-3"
    posiciones: List[PosicionVacia]  # 11 posiciones vacías
    club_actual: ClubActual  # Club que deben adivinar
    entrenador_apellido: str  # Apellido del DT a adivinar
    entrenador_nombre_completo: str
    entrenador_revelado: bool = False
    jugadores_revelados: int = 0  # Contador
    pistas_disponibles: int = 3


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
    posicion_asignada: Optional[str] = None
    nuevo_club: Optional[Dict[str, Any]] = None  # Siguiente club a adivinar
    elementos_revelados: Optional[List[str]] = None
    pista_nueva: Optional[str] = None
    game_over: bool = False
    victoria: bool = False
