"""
Servicio para manejo de imágenes
"""

import os
import re
from pathlib import Path
from typing import Optional
from ..config import Settings
from ..utils import HTTPClient, TextUtils


class ImageService:
    """
    Servicio para descarga y gestión de imágenes de jugadores
    """
    
    def __init__(self, settings: Optional[Settings] = None, http_client: Optional[HTTPClient] = None):
        """
        Inicializa el servicio de imágenes
        
        Args:
            settings: Instancia de Settings (opcional)
            http_client: Cliente HTTP (opcional)
        """
        self.settings = settings or Settings()
        self.http_client = http_client or HTTPClient(self.settings)
    
    def descargar_imagen(self, url_imagen: str, nombre_jugador: str) -> Optional[str]:
        """
        Descarga la imagen del perfil del jugador
        
        Args:
            url_imagen: URL de la imagen
            nombre_jugador: Nombre del jugador
        
        Returns:
            Ruta relativa de la imagen descargada o None si falla
        """
        try:
            if not url_imagen or url_imagen == self.settings.TRANSFERMARKT_BASE_URL:
                return None
            
            # Limpiar nombre para archivo
            nombre_archivo = TextUtils.limpiar_nombre_archivo(nombre_jugador)
            
            # Obtener extensión de la imagen
            extension = self._extraer_extension(url_imagen)
            
            # Ruta completa y relativa
            ruta_completa = self.settings.IMAGES_DIR / f"{nombre_archivo}{extension}"
            ruta_relativa = f"data/images/{nombre_archivo}{extension}"
            
            # Si ya existe la imagen, no descargar de nuevo
            if ruta_completa.exists():
                return ruta_relativa
            
            # Descargar imagen
            response = self.http_client.get(url_imagen)
            
            # Guardar imagen
            with open(ruta_completa, 'wb') as f:
                f.write(response.content)
            
            return ruta_relativa
        
        except Exception as e:
            print(f"      ⚠️  Error descargando imagen: {e}")
            return None
    
    def _extraer_extension(self, url: str) -> str:
        """
        Extrae la extensión de la imagen desde la URL
        
        Args:
            url: URL de la imagen
        
        Returns:
            Extensión con punto (ej: '.jpg')
        """
        extension = '.jpg'  # Default
        if '.' in url:
            ext_match = re.search(r'\.(jpg|jpeg|png|gif|webp)', url.lower())
            if ext_match:
                extension = '.' + ext_match.group(1)
        return extension
    
    def imagen_existe(self, nombre_jugador: str) -> bool:
        """
        Verifica si ya existe una imagen para el jugador
        
        Args:
            nombre_jugador: Nombre del jugador
        
        Returns:
            True si existe, False si no
        """
        nombre_archivo = TextUtils.limpiar_nombre_archivo(nombre_jugador)
        # Buscar con cualquier extensión
        for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
            if (self.settings.IMAGES_DIR / f"{nombre_archivo}{ext}").exists():
                return True
        return False
