"""
Modelo de datos para Jugador
"""

from dataclasses import dataclass, asdict, field
from typing import Optional, List, Dict


@dataclass
class Club:
    """
    Representa un club en la historia del jugador
    
    Attributes:
        nombre: Nombre del club
        pais: País del club
        periodo: Período en el club (ej: "2015 - 2018")
    """
    nombre: str
    pais: str
    periodo: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convierte el club a diccionario"""
        return asdict(self)


@dataclass
class Jugador:
    """
    Representa un jugador de Rosario Central
    
    Attributes:
        nombre: Nombre completo del jugador
        nacionalidad: País de origen
        posicion: Posición específica en el campo
        partidos: Número de partidos jugados
        image_profile: Ruta a la imagen de perfil (opcional)
        clubes_historia: Lista de clubes donde jugó (opcional)
        tarjetas_por_torneo: Lista de tarjetas por torneo en Rosario Central (opcional)
        goles_por_torneo: Lista de goles, partidos y minutos por torneo en Rosario Central (opcional)
        url_perfil: URL del perfil en Transfermarkt (opcional)
        fuente: Fuente de los datos (ej: 'Transfermarkt')
    """
    
    nombre: str
    nacionalidad: str
    posicion: str
    partidos: int
    image_profile: Optional[str] = None
    clubes_historia: Optional[List[Dict]] = None
    tarjetas_por_torneo: Optional[List[Dict]] = None
    goles_por_torneo: Optional[List[Dict]] = None
    url_perfil: Optional[str] = None
    fuente: str = 'Transfermarkt (Completo)'
    
    def to_dict(self) -> dict:
        """Convierte el jugador a diccionario"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Jugador':
        """Crea un jugador desde un diccionario"""
        return cls(**data)
    
    def tiene_historia_clubes(self) -> bool:
        """Verifica si ya tiene la historia de clubes completa"""
        return self.clubes_historia is not None and len(self.clubes_historia) > 0
    
    def __str__(self):
        clubes_info = f" - {len(self.clubes_historia)} clubes" if self.clubes_historia else ""
        return f"{self.nombre} ({self.nacionalidad}) - {self.posicion} - {self.partidos} partidos{clubes_info}"
    
    def __repr__(self):
        return f"Jugador(nombre='{self.nombre}', partidos={self.partidos})"
