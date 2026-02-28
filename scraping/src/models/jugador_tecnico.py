"""
Modelos de datos para jugadores dirigidos por técnicos.
"""

from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class JugadorBajoTecnico:
    """Representa un jugador y sus estadísticas bajo un técnico específico."""
    
    nombre: str
    nacionalidad: str
    posicion: str
    apariciones: int
    goles: int
    asistencias: int
    minutos: int = 0
    url_perfil: str = ""
    
    def to_dict(self) -> dict:
        return {
            'nombre': self.nombre,
            'nacionalidad': self.nacionalidad,
            'posicion': self.posicion,
            'apariciones': self.apariciones,
            'goles': self.goles,
            'asistencias': self.asistencias,
            'minutos': self.minutos,
            'url_perfil': self.url_perfil
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'JugadorBajoTecnico':
        return cls(
            nombre=data.get('nombre', ''),
            nacionalidad=data.get('nacionalidad', ''),
            posicion=data.get('posicion', ''),
            apariciones=data.get('apariciones', 0),
            goles=data.get('goles', 0),
            asistencias=data.get('asistencias', 0),
            minutos=data.get('minutos', 0),
            url_perfil=data.get('url_perfil', '')
        )


@dataclass
class JugadoresPorTorneo:
    """Agrupa jugadores dirigidos en un torneo específico."""
    
    torneo: str
    temporada: str
    total_jugadores: int = 0
    jugadores: List[JugadorBajoTecnico] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        return {
            'torneo': self.torneo,
            'temporada': self.temporada,
            'total_jugadores': self.total_jugadores,
            'jugadores': [j.to_dict() for j in self.jugadores]
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'JugadoresPorTorneo':
        jugadores = [JugadorBajoTecnico.from_dict(j) for j in data.get('jugadores', [])]
        return cls(
            torneo=data.get('torneo', ''),
            temporada=data.get('temporada', ''),
            total_jugadores=data.get('total_jugadores', 0),
            jugadores=jugadores
        )


@dataclass
class ResumenJugador:
    """Resumen de un jugador dirigido por un técnico (todas las temporadas)."""
    
    nombre: str
    total_apariciones: int
    total_goles: int
    total_asistencias: int
    total_minutos: int
    temporadas: int  # Cantidad de temporadas dirigidas
    
    def to_dict(self) -> dict:
        return {
            'nombre': self.nombre,
            'total_apariciones': self.total_apariciones,
            'total_goles': self.total_goles,
            'total_asistencias': self.total_asistencias,
            'total_minutos': self.total_minutos,
            'temporadas': self.temporadas
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ResumenJugador':
        return cls(
            nombre=data.get('nombre', ''),
            total_apariciones=data.get('total_apariciones', 0),
            total_goles=data.get('total_goles', 0),
            total_asistencias=data.get('total_asistencias', 0),
            total_minutos=data.get('total_minutos', 0),
            temporadas=data.get('temporadas', 0)
        )


@dataclass
class JugadoresTecnico:
    """Estructura completa de jugadores dirigidos por un técnico."""
    
    nombre_tecnico: str
    url_perfil: str
    torneos: List[JugadoresPorTorneo] = field(default_factory=list)
    jugadores_mas_dirigidos: List[ResumenJugador] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        return {
            'url_perfil': self.url_perfil,
            'total_torneos': len(self.torneos),
            'jugadores_mas_dirigidos': [j.to_dict() for j in self.jugadores_mas_dirigidos],
            'torneos': [t.to_dict() for t in self.torneos]
        }
    
    @classmethod
    def from_dict(cls, nombre: str, data: dict) -> 'JugadoresTecnico':
        torneos = [JugadoresPorTorneo.from_dict(t) for t in data.get('torneos', [])]
        jugadores_mas_dirigidos = [
            ResumenJugador.from_dict(j) 
            for j in data.get('jugadores_mas_dirigidos', [])
        ]
        return cls(
            nombre_tecnico=nombre,
            url_perfil=data.get('url_perfil', ''),
            torneos=torneos,
            jugadores_mas_dirigidos=jugadores_mas_dirigidos
        )
