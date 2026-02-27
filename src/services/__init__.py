"""Módulo de servicios"""

from .image_service import ImageService
from .storage_service import StorageService
from .club_history_service import ClubHistoryService
from .stats_service import StatsService
from .goles_detallados_service import GolesDetalladosService

__all__ = ['ImageService', 'StorageService', 'ClubHistoryService', 'StatsService', 'GolesDetalladosService']
