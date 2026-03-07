"""
Modelo de datos para partidos clásicos Rosario Central vs Newell's Old Boys
Optimizado para uso en FastAPI y el juego de adivinanza de formaciones
"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any


@dataclass
class Arbitro:
    """Árbitro del partido"""
    nombre: str
    apellido: str
    nombre_completo: str
    nacionalidad: Optional[str] = None
    foto_url: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "nombre": self.nombre,
            "apellido": self.apellido,
            "nombre_completo": self.nombre_completo,
            "nacionalidad": self.nacionalidad,
            "foto_url": self.foto_url
        }


@dataclass
class JugadorPartido:
    """Jugador en un partido específico"""
    numero: int
    nombre: str
    apellido: str
    nombre_completo: str
    posicion: str  # DEL, MC, DC, etc.
    titular: bool
    foto_url: Optional[str] = None
    
    # Estadísticas del partido
    goles: int = 0
    asistencias: int = 0
    tarjetas_amarillas: int = 0
    tarjetas_rojas: int = 0
    sustituido: bool = False
    minuto_sustitucion: Optional[int] = None
    ingreso: bool = False  # Si entró como suplente
    minuto_ingreso: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "numero": self.numero,
            "nombre": self.nombre,
            "apellido": self.apellido,
            "nombre_completo": self.nombre_completo,
            "posicion": self.posicion,
            "titular": self.titular,
            "foto_url": self.foto_url,
            "goles": self.goles,
            "asistencias": self.asistencias,
            "tarjetas_amarillas": self.tarjetas_amarillas,
            "tarjetas_rojas": self.tarjetas_rojas,
            "sustituido": self.sustituido,
            "minuto_sustitucion": self.minuto_sustitucion,
            "ingreso": self.ingreso,
            "minuto_ingreso": self.minuto_ingreso
        }


@dataclass
class Entrenador:
    """Entrenador del equipo"""
    nombre: str
    apellido: str
    nombre_completo: str
    nacionalidad: Optional[str] = None
    foto_url: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "nombre": self.nombre,
            "apellido": self.apellido,
            "nombre_completo": self.nombre_completo,
            "nacionalidad": self.nacionalidad,
            "foto_url": self.foto_url
        }


@dataclass
class Gol:
    """Gol anotado en el partido"""
    jugador_apellido: str
    jugador_nombre_completo: str
    minuto: str  # Puede ser "45+2", "90+3", etc.
    tipo: str = "gol"  # "gol", "penal", "autogol"
    jugador_nombre: Optional[str] = None
    asistencia_apellido: Optional[str] = None
    asistencia_nombre: Optional[str] = None
    asistencia_nombre_completo: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "jugador_apellido": self.jugador_apellido,
            "jugador_nombre": self.jugador_nombre,
            "jugador_nombre_completo": self.jugador_nombre_completo,
            "minuto": self.minuto,
            "tipo": self.tipo,
            "asistencia_apellido": self.asistencia_apellido,
            "asistencia_nombre": self.asistencia_nombre,
            "asistencia_nombre_completo": self.asistencia_nombre_completo
        }


@dataclass
class FormacionEquipo:
    """Formación del equipo en el partido"""
    esquema: str  # "4-3-3", "4-2-3-1", "3-5-2", etc.
    entrenador: Entrenador
    jugadores_titulares: List[JugadorPartido] = field(default_factory=list)
    jugadores_suplentes: List[JugadorPartido] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "esquema": self.esquema,
            "entrenador": self.entrenador.to_dict(),
            "jugadores_titulares": [j.to_dict() for j in self.jugadores_titulares],
            "jugadores_suplentes": [j.to_dict() for j in self.jugadores_suplentes],
            "total_titulares": len(self.jugadores_titulares),
            "total_suplentes": len(self.jugadores_suplentes)
        }


@dataclass
class PartidoClasico:
    """
    Partido clásico entre Rosario Central y Newell's Old Boys
    Optimizado para el juego de adivinanza de formaciones
    """
    partido_id: str  # ID de Transfermarkt (ej: "4529533")
    fecha: str  # "2025-02-15"
    competicion: str  # "Torneo Inicial", "Copa Libertadores", etc.
    jornada: str  # "6", "Semifinal", etc.
    
    # Equipos
    local: str  # "Rosario Central" o "Newell's Old Boys"
    visitante: str
    
    # Resultado
    resultado: str  # "1:2"
    goles_local: int
    goles_visitante: int
    
    # Detalles del partido
    estadio: Optional[str] = None
    espectadores: Optional[str] = None
    arbitro: Optional[Arbitro] = None
    
    # Formaciones (solo guardamos la de Rosario Central)
    rosario_central_local: bool = True  # True si RC jugó de local
    formacion_rosario_central: Optional[FormacionEquipo] = None
    
    # Goles (solo de Rosario Central)
    goles_rosario_central: List[Gol] = field(default_factory=list)
    
    # URL del partido en Transfermarkt
    url_partido: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convierte a diccionario optimizado para FastAPI
        """
        data = {
            "partido_id": self.partido_id,
            "fecha": self.fecha,
            "competicion": self.competicion,
            "jornada": self.jornada,
            "local": self.local,
            "visitante": self.visitante,
            "resultado": self.resultado,
            "goles_local": self.goles_local,
            "goles_visitante": self.goles_visitante,
            "estadio": self.estadio,
            "espectadores": self.espectadores,
            "rosario_central_local": self.rosario_central_local,
            "url_partido": self.url_partido
        }
        
        # Añadir árbitro si existe
        if self.arbitro:
            data["arbitro"] = self.arbitro.to_dict()
        
        # Añadir formación de Rosario Central
        if self.formacion_rosario_central:
            data["formacion"] = self.formacion_rosario_central.to_dict()
        
        # Añadir goles de Rosario Central
        data["goles"] = [g.to_dict() for g in self.goles_rosario_central]
        data["total_goles_rosario_central"] = len(self.goles_rosario_central)
        
        # Información útil para el juego
        data["game_data"] = {
            "total_jugadores_adivinar": 11,  # Siempre 11 titulares
            "esquema": self.formacion_rosario_central.esquema if self.formacion_rosario_central else None,
            "entrenador_apellido": self.formacion_rosario_central.entrenador.apellido if self.formacion_rosario_central else None,
            "tiene_goles": len(self.goles_rosario_central) > 0,
            "goleadores_apellidos": [g.jugador_apellido for g in self.goles_rosario_central]
        }
        
        return data


@dataclass
class ClasicosCollection:
    """Colección de todos los partidos clásicos scrapeados"""
    partidos: List[PartidoClasico] = field(default_factory=list)
    total_partidos: int = 0
    ultima_actualizacion: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "partidos": [p.to_dict() for p in self.partidos],
            "total_partidos": len(self.partidos),
            "ultima_actualizacion": self.ultima_actualizacion,
            "estadisticas": {
                "partidos_con_formacion": sum(1 for p in self.partidos if p.formacion_rosario_central),
                "partidos_con_arbitro": sum(1 for p in self.partidos if p.arbitro),
                "total_goles_rosario_central": sum(len(p.goles_rosario_central) for p in self.partidos)
            }
        }
    
    def add_partido(self, partido: PartidoClasico):
        """Añade un partido a la colección"""
        self.partidos.append(partido)
        self.total_partidos = len(self.partidos)
