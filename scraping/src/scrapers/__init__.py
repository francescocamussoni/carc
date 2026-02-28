"""Módulo de scrapers"""

from .base_scraper import BaseScraper
from .transfermarkt_scraper import TransfermarktScraper
from .tecnico_scraper import TecnicoScraper
from .tecnico_jugadores_scraper import TecnicoJugadoresScraper

__all__ = [
    'BaseScraper', 
    'TransfermarktScraper',
    'TecnicoScraper',
    'TecnicoJugadoresScraper'
]
