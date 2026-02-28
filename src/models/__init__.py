"""Módulo de modelos de datos"""

from .jugador import Jugador
from .gol_detallado import GolIndividual, GolesJugador
from .tecnico import Tecnico, ClubTecnico, EstadisticaTorneo, InfoRosario, PeriodoRosario
from .jugador_tecnico import JugadorBajoTecnico, JugadoresPorTorneo, JugadoresTecnico, ResumenJugador

__all__ = [
    'Jugador', 
    'GolIndividual', 
    'GolesJugador',
    'Tecnico',
    'ClubTecnico',
    'EstadisticaTorneo',
    'InfoRosario',
    'PeriodoRosario',
    'JugadorBajoTecnico',
    'JugadoresPorTorneo',
    'JugadoresTecnico',
    'ResumenJugador'
]
