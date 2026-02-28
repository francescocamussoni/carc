"""
Core configuration for the application
"""
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field
import os
from pathlib import Path


class Settings(BaseSettings):
    """Application settings"""
    
    # API Configuration
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "FutFactos Rosario Central"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8080"
    ]
    
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./carc_futfactos.db"
    
    # Base directories
    BASE_DIR: str = str(Path(__file__).parent.parent.parent.parent)
    DATA_DIR: str = str(Path(__file__).parent.parent.parent.parent / "scraping" / "data" / "output")
    IMAGES_DIR: str = str(Path(__file__).parent.parent.parent.parent / "scraping" / "data" / "images")
    
    # Data file paths
    JUGADORES_FILE: str = str(Path(__file__).parent.parent.parent.parent / "scraping" / "data" / "output" / "rosario_central_jugadores.json")
    TECNICOS_FILE: str = str(Path(__file__).parent.parent.parent.parent / "scraping" / "data" / "output" / "rosario_central_tecnicos.json")
    TECNICOS_JUGADORES_FILE: str = str(Path(__file__).parent.parent.parent.parent / "scraping" / "data" / "output" / "rosario_central_tecnicos_jugadores.json")
    GOLES_DETALLADOS_FILE: str = str(Path(__file__).parent.parent.parent.parent / "scraping" / "data" / "output" / "rosario_central_goles_detallados.json")
    
    # Game settings
    GAME_REFRESH_HOUR: int = 0  # Midnight
    TIMEZONE: str = "America/Argentina/Buenos_Aires"
    
    class Config:
        case_sensitive = True
        env_file = ".env"


# Singleton instance
settings = Settings()
