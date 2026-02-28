"""
Servicio para descargar y gestionar imágenes de técnicos
"""

import os
import re
from pathlib import Path
from typing import Optional
from bs4 import BeautifulSoup

from ..config import Settings
from ..utils import HTTPClient


class TecnicoImageService:
    """
    Servicio para descargar y guardar imágenes de perfil de técnicos
    """
    
    def __init__(self, settings: Optional[Settings] = None, http_client: Optional[HTTPClient] = None):
        """
        Inicializa el servicio
        
        Args:
            settings: Instancia de Settings (opcional)
            http_client: Cliente HTTP (opcional)
        """
        self.settings = settings or Settings()
        self.http_client = http_client or HTTPClient(self.settings)
    
    def descargar_imagen_tecnico(self, url_perfil: str, nombre_tecnico: str) -> str:
        """
        Descarga la imagen de perfil de un técnico
        
        Args:
            url_perfil: URL del perfil del técnico
            nombre_tecnico: Nombre del técnico
        
        Returns:
            Ruta relativa de la imagen guardada o cadena vacía si falla
        """
        try:
            print(f"      📷 Descargando foto...")
            
            # Obtener HTML del perfil
            url_completa = f"{self.settings.TRANSFERMARKT_BASE_URL}{url_perfil}"
            response = self.http_client.get(url_completa, use_cache=True)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Buscar la imagen del perfil
            url_imagen = self._extraer_url_imagen(soup)
            
            if not url_imagen:
                print(f"      ℹ️  No se encontró imagen de perfil")
                return ""
            
            # Descargar imagen
            imagen_response = self.http_client.get(url_imagen)
            
            if imagen_response.status_code != 200:
                print(f"      ⚠️  Error descargando imagen: {imagen_response.status_code}")
                return ""
            
            # Generar nombre de archivo
            nombre_archivo = self._generar_nombre_archivo(nombre_tecnico, url_imagen)
            ruta_completa = self.settings.TECNICOS_IMAGES_DIR / nombre_archivo
            
            # Guardar imagen
            with open(ruta_completa, 'wb') as f:
                f.write(imagen_response.content)
            
            # Retornar ruta relativa
            ruta_relativa = f"data/images/tecnicos/{nombre_archivo}"
            print(f"      ✅ Imagen guardada: {nombre_archivo}")
            
            return ruta_relativa
        
        except Exception as e:
            print(f"      ⚠️  Error descargando imagen: {e}")
            return ""
    
    def _extraer_url_imagen(self, soup) -> str:
        """Extrae la URL de la imagen de perfil"""
        try:
            # Buscar imagen en el header del perfil
            img = soup.find('img', class_='data-header__profile-image')
            if img:
                return img.get('src', '')
            
            # Método alternativo: buscar en cualquier div con clase de imagen
            divs_imagen = soup.find_all('div', class_=re.compile(r'data-header__profile'))
            for div in divs_imagen:
                img = div.find('img')
                if img:
                    return img.get('src', '')
        
        except Exception:
            pass
        
        return ""
    
    def _generar_nombre_archivo(self, nombre: str, url_imagen: str) -> str:
        """
        Genera un nombre de archivo normalizado para la imagen
        
        Args:
            nombre: Nombre del técnico
            url_imagen: URL de la imagen (para obtener extensión)
        
        Returns:
            Nombre de archivo normalizado
        """
        # Normalizar nombre
        nombre_limpio = nombre.lower()
        nombre_limpio = re.sub(r'[^a-z0-9]+', '_', nombre_limpio)
        nombre_limpio = nombre_limpio.strip('_')
        
        # Obtener extensión de la URL
        extension = self._obtener_extension(url_imagen)
        
        return f"{nombre_limpio}{extension}"
    
    def _obtener_extension(self, url: str) -> str:
        """Obtiene la extensión del archivo desde la URL"""
        extensiones_validas = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
        
        url_lower = url.lower()
        for ext in extensiones_validas:
            if ext in url_lower:
                return ext
        
        # Por defecto, usar .jpg
        return '.jpg'
