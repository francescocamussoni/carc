"""
Configuración centralizada del scraper (Singleton Pattern)
"""

import os
from pathlib import Path


class Settings:
    """
    Configuración centralizada usando Singleton Pattern
    Garantiza una única instancia de configuración en toda la aplicación
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Settings, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Inicializa las configuraciones por defecto"""
        
        # Rutas base
        self.BASE_DIR = Path(__file__).parent.parent.parent
        self.DATA_DIR = self.BASE_DIR / 'data'
        self.OUTPUT_DIR = self.DATA_DIR / 'output'
        self.IMAGES_DIR = self.DATA_DIR / 'images'
        self.TECNICOS_IMAGES_DIR = self.IMAGES_DIR / 'tecnicos'
        
        # Crear directorios si no existen
        self.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        self.IMAGES_DIR.mkdir(parents=True, exist_ok=True)
        self.TECNICOS_IMAGES_DIR.mkdir(parents=True, exist_ok=True)
        
        # Configuración de scraping
        self.MIN_PARTIDOS = 2
        self.MAX_PAGINAS = 19
        self.MAX_RETRIES = 3
        self.RETRY_DELAY = 2  # segundos
        
        # Delays para evitar rate limiting
        self.DELAY_ENTRE_JUGADORES = (0.3, 0.8)  # (min, max) segundos - reducido por paralelización
        self.DELAY_ENTRE_PAGINAS = (1, 2)  # (min, max) segundos - reducido por paralelización
        
        # Configuración de paralelización
        self.MAX_WORKERS = 10  # Número de threads paralelos
        self.BATCH_SAVE_SIZE = 5  # Guardar cada N jugadores
        self.USE_SESSION_POOL = True  # Reutilizar conexiones HTTP
        
        # Headers HTTP
        self.HEADERS = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        # URLs de Transfermarkt
        self.TRANSFERMARKT_BASE_URL = 'https://www.transfermarkt.es'
        self.TRANSFERMARKT_CLUB_ID = '1418'  # Rosario Central
        self.TRANSFERMARKT_REKORDSPIELER_URL = f'{self.TRANSFERMARKT_BASE_URL}/club-atletico-rosario-central/rekordspieler/verein/{self.TRANSFERMARKT_CLUB_ID}'
        self.TRANSFERMARKT_MITARBEITER_URL = f'{self.TRANSFERMARKT_BASE_URL}/club-atletico-rosario-central/mitarbeiterhistorie/verein/{self.TRANSFERMARKT_CLUB_ID}'
        
        # Archivos de salida
        self.JSON_OUTPUT = self.OUTPUT_DIR / 'rosario_central_jugadores.json'
        self.CSV_OUTPUT = self.OUTPUT_DIR / 'rosario_central_jugadores.csv'
        self.GOLES_DETALLADOS_OUTPUT = self.OUTPUT_DIR / 'rosario_central_goles_detallados.json'
        self.TECNICOS_OUTPUT = self.OUTPUT_DIR / 'rosario_central_tecnicos.json'
        self.TECNICOS_JUGADORES_OUTPUT = self.OUTPUT_DIR / 'rosario_central_tecnicos_jugadores.json'
    
    def update(self, **kwargs):
        """
        Actualiza configuraciones dinámicamente
        
        Args:
            **kwargs: Pares clave-valor de configuraciones a actualizar
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                raise AttributeError(f"Settings no tiene el atributo '{key}'")
    
    def __repr__(self):
        return f"<Settings(MIN_PARTIDOS={self.MIN_PARTIDOS}, MAX_RETRIES={self.MAX_RETRIES})>"
