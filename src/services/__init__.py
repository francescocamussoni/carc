"""Módulo de servicios"""

from .image_service import ImageService
from .storage_service import StorageService
from .club_history_service import ClubHistoryService
from .stats_service import StatsService
from .goles_detallados_service import GolesDetalladosService
from .tecnico_service import TecnicoService
from .tecnico_clubes_service import TecnicoClubesService
from .tecnico_stats_service import TecnicoStatsService
from .tecnico_image_service import TecnicoImageService

__all__ = [
    'ImageService', 
    'StorageService', 
    'ClubHistoryService', 
    'StatsService', 
    'GolesDetalladosService',
    'TecnicoService',
    'TecnicoClubesService',
    'TecnicoStatsService',
    'TecnicoImageService'
]
