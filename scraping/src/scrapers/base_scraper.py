"""
Clase base abstracta para scrapers (Strategy Pattern)
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from ..models import Jugador
from ..config import Settings
from ..services import StorageService, ImageService, ClubHistoryService, StatsService
from ..utils import HTTPClient


class BaseScraper(ABC):
    """
    Clase base abstracta para todos los scrapers
    Implementa el Strategy Pattern para permitir diferentes fuentes de datos
    """
    
    def __init__(
        self, 
        settings: Optional[Settings] = None,
        storage_service: Optional[StorageService] = None,
        image_service: Optional[ImageService] = None,
        http_client: Optional[HTTPClient] = None,
        club_history_service: Optional[ClubHistoryService] = None,
        stats_service: Optional[StatsService] = None
    ):
        """
        Inicializa el scraper base
        
        Args:
            settings: Configuración (opcional)
            storage_service: Servicio de almacenamiento (opcional)
            image_service: Servicio de imágenes (opcional)
            http_client: Cliente HTTP (opcional)
            club_history_service: Servicio de historia de clubes (opcional)
            stats_service: Servicio de estadísticas (opcional)
        """
        self.settings = settings or Settings()
        self.http_client = http_client or HTTPClient(self.settings)
        self.storage = storage_service or StorageService(self.settings)
        self.image_service = image_service or ImageService(self.settings, self.http_client)
        self.club_history = club_history_service or ClubHistoryService(self.settings, self.http_client)
        self.stats_service = stats_service or StatsService(self.settings, self.http_client)
    
    @abstractmethod
    def scrape(self) -> List[Jugador]:
        """
        Método abstracto que debe implementar cada scraper
        
        Returns:
            Lista de jugadores scrappeados
        """
        pass
    
    @abstractmethod
    def get_source_name(self) -> str:
        """
        Retorna el nombre de la fuente de datos
        
        Returns:
            Nombre de la fuente
        """
        pass
    
    def run(self) -> List[Jugador]:
        """
        Ejecuta el scraping completo con manejo de errores
        
        Returns:
            Lista de jugadores scrappeados
        """
        print(f"\n🔍 Iniciando scraping desde {self.get_source_name()}...")
        
        try:
            # Cargar jugadores existentes
            self.storage.cargar_jugadores_existentes()
            
            # Ejecutar scraping
            jugadores = self.scrape()
            
            # Guardar resultados finales
            print(f"\n💾 Guardando resultados finales...")
            if self.storage.guardar_json():
                print(f"   ✅ JSON guardado: {self.settings.JSON_OUTPUT}")
            if self.storage.guardar_csv():
                print(f"   ✅ CSV guardado: {self.settings.CSV_OUTPUT}")
            
            return jugadores
        
        except KeyboardInterrupt:
            print(f"\n\n⚠️  Scraping interrumpido por el usuario")
            print(f"💾 Guardando {len(self.storage.jugadores)} jugadores obtenidos hasta ahora...")
            self.storage.guardar_json()
            self.storage.guardar_csv()
            return self.storage.jugadores
        
        except Exception as e:
            print(f"\n❌ Error durante el scraping: {e}")
            print(f"💾 Guardando {len(self.storage.jugadores)} jugadores obtenidos hasta ahora...")
            self.storage.guardar_json()
            self.storage.guardar_csv()
            raise
