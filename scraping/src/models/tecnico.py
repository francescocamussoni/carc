"""
Modelo para representar un técnico/entrenador
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional


@dataclass
class PeriodoRosario:
    """
    Representa un periodo específico del técnico en Rosario Central
    
    Attributes:
        periodo: Fechas del periodo (ej: "01/07/2020 - 30/06/2021")
        partidos_dirigidos: Cantidad de partidos dirigidos en este periodo
    """
    periodo: str
    partidos_dirigidos: int
    
    def to_dict(self) -> dict:
        return {
            'periodo': self.periodo,
            'partidos_dirigidos': self.partidos_dirigidos
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'PeriodoRosario':
        return cls(**data)


@dataclass
class InfoRosario:
    """
    Información completa sobre los pasos del técnico por Rosario Central
    
    Attributes:
        periodos: Lista de periodos que dirigió el club
        total_periodos: Cantidad total de periodos
        total_partidos: Total de partidos dirigidos sumando todos los periodos
    """
    periodos: List[PeriodoRosario] = field(default_factory=list)
    total_periodos: int = 0
    total_partidos: int = 0
    
    def to_dict(self) -> dict:
        return {
            'periodos': [p.to_dict() for p in self.periodos],
            'total': {
                'periodos': self.total_periodos,
                'partidos': self.total_partidos
            }
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'InfoRosario':
        periodos = [PeriodoRosario.from_dict(p) for p in data.get('periodos', [])]
        total_info = data.get('total', {})
        return cls(
            periodos=periodos,
            total_periodos=total_info.get('periodos', 0),
            total_partidos=total_info.get('partidos', 0)
        )


@dataclass
class ClubTecnico:
    """
    Representa un club que dirigió el técnico
    
    Attributes:
        club: Nombre del club
        pais: País del club
        periodo: Periodo que dirigió (ej: "01/07/2020 - 30/06/2021")
    """
    club: str
    pais: str
    periodo: str
    
    def to_dict(self) -> dict:
        return {
            'club': self.club,
            'pais': self.pais,
            'periodo': self.periodo
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ClubTecnico':
        return cls(**data)


@dataclass
class EstadisticaTorneo:
    """
    Representa estadísticas de un técnico en un torneo específico
    
    Attributes:
        torneo: Nombre del torneo
        temporada: Temporada (ej: "2023/2024")
        partidos: Total de partidos dirigidos
        victorias: Cantidad de victorias
        empates: Cantidad de empates
        derrotas: Cantidad de derrotas
    """
    torneo: str
    temporada: str
    partidos: int
    victorias: int
    empates: int
    derrotas: int
    
    def to_dict(self) -> dict:
        return {
            'torneo': self.torneo,
            'temporada': self.temporada,
            'partidos': self.partidos,
            'victorias': self.victorias,
            'empates': self.empates,
            'derrotas': self.derrotas
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'EstadisticaTorneo':
        return cls(**data)


@dataclass
class Tecnico:
    """
    Representa un técnico/entrenador de Rosario Central
    
    Attributes:
        nombre: Nombre completo del técnico
        url_perfil: URL del perfil en Transfermarkt
        nacionalidad: Nacionalidad del técnico
        fecha_nacimiento: Fecha de nacimiento (opcional)
        edad: Edad actual (opcional)
        image_profile: Ruta local de la foto del técnico
        info_rosario: Información completa sobre sus pasos por Rosario Central
        clubes_historia: Lista de todos los clubes que dirigió
        estadisticas_por_torneo: Estadísticas por torneo en Rosario Central
    """
    nombre: str
    url_perfil: str
    nacionalidad: str = ""
    fecha_nacimiento: str = ""
    edad: str = ""
    image_profile: str = ""
    info_rosario: InfoRosario = field(default_factory=InfoRosario)
    clubes_historia: List[ClubTecnico] = field(default_factory=list)
    estadisticas_por_torneo: List[EstadisticaTorneo] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        """Convierte el técnico a diccionario"""
        return {
            'url_perfil': self.url_perfil,
            'nacionalidad': self.nacionalidad,
            'fecha_nacimiento': self.fecha_nacimiento,
            'edad': self.edad,
            'image_profile': self.image_profile,
            'info_rosario': self.info_rosario.to_dict(),
            'clubes_historia': [c.to_dict() for c in self.clubes_historia],
            'estadisticas_por_torneo': [e.to_dict() for e in self.estadisticas_por_torneo]
        }
    
    @classmethod
    def from_dict(cls, nombre: str, data: dict) -> 'Tecnico':
        """Crea un técnico desde un diccionario"""
        clubes = [ClubTecnico.from_dict(c) for c in data.get('clubes_historia', [])]
        estadisticas = [EstadisticaTorneo.from_dict(e) for e in data.get('estadisticas_por_torneo', [])]
        
        # Manejar retrocompatibilidad con formato anterior
        info_rosario_data = data.get('info_rosario')
        if info_rosario_data:
            info_rosario = InfoRosario.from_dict(info_rosario_data)
        else:
            # Formato anterior: periodo_rosario y partidos_dirigidos
            periodo_anterior = data.get('periodo_rosario', '')
            partidos_anterior = data.get('partidos_dirigidos', 0)
            if periodo_anterior:
                info_rosario = InfoRosario(
                    periodos=[PeriodoRosario(periodo=periodo_anterior, partidos_dirigidos=partidos_anterior)],
                    total_periodos=1,
                    total_partidos=partidos_anterior
                )
            else:
                info_rosario = InfoRosario()
        
        return cls(
            nombre=nombre,
            url_perfil=data.get('url_perfil', ''),
            nacionalidad=data.get('nacionalidad', ''),
            fecha_nacimiento=data.get('fecha_nacimiento', ''),
            edad=data.get('edad', ''),
            image_profile=data.get('image_profile', ''),
            info_rosario=info_rosario,
            clubes_historia=clubes,
            estadisticas_por_torneo=estadisticas
        )
