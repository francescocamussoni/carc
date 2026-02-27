"""
Cliente HTTP con retry automático y backoff exponencial
"""

import requests
import time
import random
from typing import Optional, Dict
from ..config import Settings


class HTTPClient:
    """
    Cliente HTTP robusto con retry automático, session pooling y caché
    Implementa backoff exponencial para manejar rate limiting
    """
    
    def __init__(self, settings: Optional[Settings] = None):
        """
        Inicializa el cliente HTTP
        
        Args:
            settings: Instancia de Settings (opcional, usa Singleton si no se provee)
        """
        self.settings = settings or Settings()
        
        # Session para reutilizar conexiones (HTTP keep-alive)
        if self.settings.USE_SESSION_POOL:
            self.session = requests.Session()
            self.session.headers.update(self.settings.HEADERS)
        else:
            self.session = None
        
        # Caché simple para evitar requests duplicados
        self.cache: Dict[str, requests.Response] = {}
    
    def get(self, url: str, max_retries: Optional[int] = None, use_cache: bool = True) -> requests.Response:
        """
        Realiza un GET request con retry automático, session pooling y caché
        
        Args:
            url: URL a consultar
            max_retries: Número máximo de intentos (default: settings.MAX_RETRIES)
            use_cache: Si True, usa caché para evitar requests duplicados
        
        Returns:
            Response de requests
        
        Raises:
            requests.RequestException: Si todos los intentos fallan
        """
        # Verificar caché
        if use_cache and url in self.cache:
            return self.cache[url]
        
        if max_retries is None:
            max_retries = self.settings.MAX_RETRIES
        
        for intento in range(1, max_retries + 1):
            try:
                # Usar session si está disponible, sino requests normal
                if self.session:
                    response = self.session.get(url, timeout=30)
                else:
                    response = requests.get(
                        url, 
                        headers=self.settings.HEADERS, 
                        timeout=30
                    )
                
                # Si es 429 (Too Many Requests) o 503 (Service Unavailable), reintentar
                if response.status_code in [429, 503]:
                    if intento < max_retries:
                        delay = self._calculate_backoff(intento)
                        print(f"      ⚠️  HTTP {response.status_code} - Reintentando en {delay:.1f}s (intento {intento}/{max_retries})")
                        time.sleep(delay)
                        continue
                    else:
                        raise requests.RequestException(
                            f"HTTP {response.status_code} después de {max_retries} intentos"
                        )
                
                response.raise_for_status()
                
                # Guardar en caché si se solicita
                if use_cache:
                    self.cache[url] = response
                
                return response
            
            except requests.Timeout:
                if intento < max_retries:
                    delay = self._calculate_backoff(intento)
                    print(f"      ⏱️  Timeout - Reintentando en {delay:.1f}s (intento {intento}/{max_retries})")
                    time.sleep(delay)
                else:
                    raise
            
            except requests.ConnectionError:
                if intento < max_retries:
                    delay = self._calculate_backoff(intento)
                    print(f"      🔌 Error de conexión - Reintentando en {delay:.1f}s (intento {intento}/{max_retries})")
                    time.sleep(delay)
                else:
                    raise
            
            except requests.RequestException as e:
                if intento < max_retries:
                    delay = self._calculate_backoff(intento)
                    print(f"      ❌ Error: {e} - Reintentando en {delay:.1f}s (intento {intento}/{max_retries})")
                    time.sleep(delay)
                else:
                    raise
        
        raise requests.RequestException(f"Falló después de {max_retries} intentos")
    
    def _calculate_backoff(self, intento: int) -> float:
        """
        Calcula el delay usando backoff exponencial con jitter
        
        Args:
            intento: Número de intento actual
        
        Returns:
            Delay en segundos
        """
        base_delay = self.settings.RETRY_DELAY * (2 ** (intento - 1))
        jitter = random.uniform(0, 1)
        return base_delay + jitter
    
    def clear_cache(self):
        """Limpia el caché de responses"""
        self.cache.clear()
    
    def close(self):
        """Cierra la sesión HTTP"""
        if self.session:
            self.session.close()