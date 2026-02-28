"""
Servicio para extraer estadísticas de partidos de un técnico
"""

from typing import List, Optional
from bs4 import BeautifulSoup
import re

from ..config import Settings
from ..utils import HTTPClient
from ..models import EstadisticaTorneo


class TecnicoStatsService:
    """
    Servicio para obtener estadísticas de partidos dirigidos por un técnico
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
    
    def obtener_estadisticas_rosario_central(self, url_perfil: str, nombre_tecnico: str) -> List[EstadisticaTorneo]:
        """
        Obtiene estadísticas de partidos dirigidos en Rosario Central por torneo
        
        Args:
            url_perfil: URL del perfil del técnico
            nombre_tecnico: Nombre del técnico (para logging)
        
        Returns:
            Lista de EstadisticaTorneo con estadísticas por torneo
        """
        try:
            # Construir URL de estadísticas
            # De /profil/trainer/XXX a /leistungsdatentrainer/trainer/XXX
            url_stats = url_perfil.replace('/profil/', '/leistungsdatentrainer/')
            
            # Agregar filtro de club
            url_completa = f"{self.settings.TRANSFERMARKT_BASE_URL}{url_stats}/verein/{self.settings.TRANSFERMARKT_CLUB_ID}"
            
            print(f"      📊 Obteniendo estadísticas por torneo...")
            
            response = self.http_client.get(url_completa, use_cache=True)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Buscar tabla de estadísticas
            tabla = soup.find('table', class_='items')
            
            if not tabla:
                print(f"      ℹ️  No se encontró tabla de estadísticas")
                return []
            
            estadisticas = []
            tbody = tabla.find('tbody')
            
            if tbody:
                filas = tbody.find_all('tr', class_=['odd', 'even'])
                
                for fila in filas:
                    try:
                        stat = self._extraer_estadistica_de_fila(fila)
                        if stat and stat.partidos > 0:
                            estadisticas.append(stat)
                    except Exception as e:
                        continue
            
            print(f"      ✅ {len(estadisticas)} torneos con estadísticas")
            return estadisticas
        
        except Exception as e:
            print(f"      ⚠️  Error obteniendo estadísticas: {e}")
            return []
    
    def _extraer_estadistica_de_fila(self, fila) -> Optional[EstadisticaTorneo]:
        """
        Extrae estadísticas de una fila de la tabla
        
        Formato típico de columnas:
        0: Temporada
        1: Competición
        2: Partidos
        3: Victorias
        4: Empates
        5: Derrotas
        """
        try:
            celdas = fila.find_all(['td', 'th'])
            
            if len(celdas) < 5:
                return None
            
            # Celda 0: Temporada
            temporada = celdas[0].text.strip()
            
            # Celda 1: Competición
            competicion = ""
            comp_cell = celdas[1]
            
            # Buscar nombre de competición (puede estar en link o directamente en texto)
            comp_link = comp_cell.find('a')
            if comp_link:
                competicion = comp_link.text.strip()
            else:
                # Buscar en imagen (tooltip)
                img = comp_cell.find('img')
                if img:
                    competicion = img.get('title', '').strip()
            
            if not competicion:
                competicion = comp_cell.text.strip()
            
            # Celdas 2-5: Partidos, Victorias, Empates, Derrotas
            partidos = self._extraer_numero(celdas[2].text.strip())
            victorias = self._extraer_numero(celdas[3].text.strip()) if len(celdas) > 3 else 0
            empates = self._extraer_numero(celdas[4].text.strip()) if len(celdas) > 4 else 0
            derrotas = self._extraer_numero(celdas[5].text.strip()) if len(celdas) > 5 else 0
            
            if partidos > 0:
                return EstadisticaTorneo(
                    torneo=competicion,
                    temporada=temporada,
                    partidos=partidos,
                    victorias=victorias,
                    empates=empates,
                    derrotas=derrotas
                )
        
        except Exception:
            pass
        
        return None
    
    def _extraer_numero(self, texto: str) -> int:
        """Extrae un número de un texto"""
        try:
            # Remover puntos de miles y convertir
            texto = texto.replace('.', '').replace(',', '')
            match = re.search(r'\d+', texto)
            if match:
                return int(match.group())
        except:
            pass
        return 0
