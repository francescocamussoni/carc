"""
Modelo para representar goles detallados de jugadores
"""

from dataclasses import dataclass, asdict, field
from typing import List, Dict, Optional


@dataclass
class GolIndividual:
    """
    Representa un gol individual con toda su información disponible
    
    Attributes:
        rival: Equipo rival contra el que marcó
        competicion: Competición (ej: "Torneo Apertura", "Copa Libertadores")
        temporada: Temporada (ej: "2005", "2021", "Temporada 2015")
        minuto: Minuto del gol (ej: "45'", "90'+3"). Vacío si no disponible
        tipo_gol: Tipo de gol (ej: "Remate de cabeza", "Penalti"). Vacío si no disponible
        marcador_momento: Marcador cuando se hizo el gol (ej: "1:0"). Vacío si no disponible
        marcador_final: Marcador final del partido (ej: "2:1"). Vacío si no disponible
        local_visitante: "H" para local/home, "A" para visitante/away. Vacío si no disponible
    """
    rival: str
    competicion: str
    temporada: str
    minuto: str = ""
    tipo_gol: str = ""
    marcador_momento: str = ""
    marcador_final: str = ""
    local_visitante: str = ""
    
    def to_dict(self) -> dict:
        """Convierte el objeto a diccionario"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'GolIndividual':
        """Crea un objeto desde un diccionario"""
        return cls(**data)


@dataclass
class GolesJugador:
    """
    Representa todos los goles de un jugador en Rosario Central
    
    Attributes:
        nombre: Nombre del jugador
        url_perfil: URL del perfil en Transfermarkt
        total_goles: Total de goles marcados
        goles: Lista de todos los goles individuales
    """
    nombre: str
    url_perfil: str
    total_goles: int
    goles: List[GolIndividual] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        """
        Convierte el objeto a diccionario en el formato:
        {
            'url_perfil': '...',
            'total_goles': N,
            'goles': [...]
        }
        """
        return {
            'url_perfil': self.url_perfil,
            'total_goles': self.total_goles,
            'goles': [g.to_dict() for g in self.goles]
        }
    
    @classmethod
    def from_dict(cls, nombre: str, data: dict) -> 'GolesJugador':
        """Crea un objeto desde un diccionario"""
        goles = [GolIndividual.from_dict(g) for g in data.get('goles', [])]
        return cls(
            nombre=nombre,
            url_perfil=data.get('url_perfil', ''),
            total_goles=data.get('total_goles', len(goles)),
            goles=goles
        )
    
    def agregar_gol(self, gol: GolIndividual):
        """Agrega un gol a la lista"""
        self.goles.append(gol)
        self.total_goles = len(self.goles)
