"""
Modelo para la relación jugador-técnico
"""

from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class JugadorBajoTecnico:
    """
    Representa un jugador dirigido por un técnico en un torneo específico
    
    Attributes:
        nombre: Nombre del jugador
        posicion: Posición del jugador
        partidos_con_tecnico: Partidos jugados bajo la dirección de este técnico
        goles: Goles marcados (si está disponible)
        asistencias: Asistencias (si está disponible)
        minutos: Minutos jugados (si está disponible)
    """
    nombre: str
    posicion: str = ""
    partidos_con_tecnico: int = 0
    goles: int = 0
    asistencias: int = 0
    minutos: int = 0
    
    def to_dict(self) -> dict:
        return {
            'nombre': self.nombre,
            'posicion': self.posicion,
            'partidos_con_tecnico': self.partidos_con_tecnico,
            'goles': self.goles,
            'asistencias': self.asistencias,
            'minutos': self.minutos
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'JugadorBajoTecnico':
        return cls(**data)


@dataclass
class JugadoresPorTorneo:
    """
    Agrupa jugadores por torneo bajo un técnico
    
    Attributes:
        torneo: Nombre del torneo
        temporada: Temporada (ej: "2023/2024")
        jugadores: Lista de jugadores que jugaron en ese torneo
    """
    torneo: str
    temporada: str
    jugadores: List[JugadorBajoTecnico] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        return {
            'torneo': self.torneo,
            'temporada': self.temporada,
            'jugadores': [j.to_dict() for j in self.jugadores]
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'JugadoresPorTorneo':
        jugadores = [JugadorBajoTecnico.from_dict(j) for j in data.get('jugadores', [])]
        return cls(
            torneo=data.get('torneo', ''),
            temporada=data.get('temporada', ''),
            jugadores=jugadores
        )


@dataclass
class JugadoresTecnico:
    """
    Representa todos los jugadores dirigidos por un técnico
    
    Attributes:
        nombre_tecnico: Nombre del técnico
        url_perfil: URL del perfil del técnico
        total_jugadores: Total de jugadores únicos dirigidos
        jugadores_por_torneo: Lista de jugadores agrupados por torneo
    """
    nombre_tecnico: str
    url_perfil: str
    total_jugadores: int = 0
    jugadores_por_torneo: List[JugadoresPorTorneo] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        return {
            'url_perfil': self.url_perfil,
            'total_jugadores': self.total_jugadores,
            'jugadores_por_torneo': [j.to_dict() for j in self.jugadores_por_torneo]
        }
    
    @classmethod
    def from_dict(cls, nombre: str, data: dict) -> 'JugadoresTecnico':
        jugadores_por_torneo = [
            JugadoresPorTorneo.from_dict(j) 
            for j in data.get('jugadores_por_torneo', [])
        ]
        return cls(
            nombre_tecnico=nombre,
            url_perfil=data.get('url_perfil', ''),
            total_jugadores=data.get('total_jugadores', 0),
            jugadores_por_torneo=jugadores_por_torneo
        )
