"""
Servicio para extraer estadísticas de jugadores desde Transfermarkt
"""

from typing import List, Dict, Optional
from bs4 import BeautifulSoup
from ..config import Settings
from ..utils import HTTPClient


class StatsService:
    """
    Servicio para obtener estadísticas del jugador por torneo en Rosario Central:
    - Tarjetas (amarillas, doble amarillas, rojas)
    - Goles
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
    
    def obtener_tarjetas_rosario_central(self, url_perfil: str, nombre_jugador: str) -> List[Dict]:
        """
        Obtiene las tarjetas del jugador en todos los torneos de Rosario Central
        
        Args:
            url_perfil: URL del perfil del jugador (ej: /jugador/profil/spieler/12345)
            nombre_jugador: Nombre del jugador (para logging)
        
        Returns:
            Lista de diccionarios con formato:
            [
                {
                    "temporada": "2018",
                    "competicion": "Superliga",
                    "amarillas": 5,
                    "doble_amarillas": 0,
                    "rojas": 0
                },
                ...
            ]
        """
        try:
            import re
            
            # Extraer ID del jugador
            match = re.search(r'/spieler/(\d+)', url_perfil)
            if not match:
                return []
            
            spieler_id = match.group(1)
            club_id = self.settings.TRANSFERMARKT_CLUB_ID
            
            # Construir URL de estadísticas detalladas filtradas por Rosario Central
            url = f"{self.settings.TRANSFERMARKT_BASE_URL}/a/leistungsdatendetails/spieler/{spieler_id}/plus/0?saison=&verein={club_id}"
            
            response = self.http_client.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Buscar la tabla de estadísticas
            tabla = soup.find('table', class_='items')
            
            if not tabla:
                return []
            
            tbody = tabla.find('tbody')
            if not tbody:
                return []
            
            filas = tbody.find_all('tr')
            tarjetas_list = []
            
            for fila in filas:
                try:
                    celdas = fila.find_all(['td', 'th'])
                    
                    if len(celdas) < 7:
                        continue
                    
                    # Extraer temporada
                    temporada = celdas[0].text.strip()
                    
                    # Extraer competición
                    competicion = celdas[2].text.strip()
                    
                    # Extraer tarjetas (formato: "5 / 1 / -" o "- / - / -")
                    tarjetas_texto = celdas[6].text.strip()
                    
                    # Parsear tarjetas
                    amarillas, doble_amarillas, rojas = self._parsear_tarjetas(tarjetas_texto)
                    
                    # Solo agregar si hay al menos una tarjeta
                    if amarillas > 0 or doble_amarillas > 0 or rojas > 0:
                        tarjetas_list.append({
                            'temporada': temporada,
                            'competicion': competicion,
                            'amarillas': amarillas,
                            'doble_amarillas': doble_amarillas,
                            'rojas': rojas
                        })
                
                except Exception:
                    continue
            
            return tarjetas_list
        
        except Exception as e:
            print(f"      ⚠️  Error obteniendo tarjetas: {e}")
            return []
    
    def _parsear_tarjetas(self, texto: str) -> tuple:
        """
        Parsea el texto de tarjetas en formato "5 / 1 / -"
        
        Args:
            texto: Texto con formato "amarillas / doble_amarillas / rojas"
        
        Returns:
            Tupla (amarillas, doble_amarillas, rojas)
        """
        try:
            partes = texto.split('/')
            
            if len(partes) != 3:
                return (0, 0, 0)
            
            # Convertir cada parte, usando 0 si es "-" o vacío
            amarillas = self._convertir_a_numero(partes[0].strip())
            doble_amarillas = self._convertir_a_numero(partes[1].strip())
            rojas = self._convertir_a_numero(partes[2].strip())
            
            return (amarillas, doble_amarillas, rojas)
        
        except Exception:
            return (0, 0, 0)
    
    def _convertir_a_numero(self, valor: str) -> int:
        """
        Convierte un valor a número, retornando 0 si es "-" o inválido
        
        Args:
            valor: Valor a convertir
        
        Returns:
            Número entero
        """
        if not valor or valor == '-':
            return 0
        
        try:
            return int(valor)
        except ValueError:
            return 0
    
    def _extraer_minutos(self, texto: str) -> int:
        """
        Extrae los minutos jugados desde el texto
        Formato típico: "1.683'" o "1683'" o "90'"
        
        Args:
            texto: Texto con los minutos
        
        Returns:
            Minutos como número entero
        """
        if not texto or texto == '-':
            return 0
        
        try:
            # Remover el apóstrofe y los puntos de separación de miles
            minutos_limpio = texto.replace("'", "").replace(".", "").replace(",", "").strip()
            
            if minutos_limpio:
                return int(minutos_limpio)
            return 0
        
        except (ValueError, AttributeError):
            return 0
    
    def obtener_goles_rosario_central(self, url_perfil: str, nombre_jugador: str) -> List[Dict]:
        """
        Obtiene estadísticas completas del jugador por torneo en Rosario Central:
        partidos, goles, minutos, amarillas, doble amarillas y rojas
        
        Args:
            url_perfil: URL del perfil del jugador (ej: /jugador/profil/spieler/12345)
            nombre_jugador: Nombre del jugador (para logging)
        
        Returns:
            Lista de diccionarios con formato:
            [
                {
                    "temporada": "2021",
                    "competicion": "Liga Profesional",
                    "partidos": 19,
                    "goles": 15,
                    "minutos": 1683,
                    "amarillas": 4,
                    "doble_amarillas": 0,
                    "rojas": 0
                },
                ...
            ]
        """
        try:
            import re
            
            # Extraer ID del jugador
            match = re.search(r'/spieler/(\d+)', url_perfil)
            if not match:
                return []
            
            spieler_id = match.group(1)
            club_id = self.settings.TRANSFERMARKT_CLUB_ID
            
            # Construir URL de estadísticas detalladas filtradas por Rosario Central
            url = f"{self.settings.TRANSFERMARKT_BASE_URL}/a/leistungsdatendetails/spieler/{spieler_id}/plus/0?saison=&verein={club_id}"
            
            response = self.http_client.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Buscar la tabla de estadísticas
            tabla = soup.find('table', class_='items')
            
            if not tabla:
                return []
            
            tbody = tabla.find('tbody')
            if not tbody:
                return []
            
            filas = tbody.find_all('tr')
            stats_list = []
            
            for fila in filas:
                try:
                    celdas = fila.find_all(['td', 'th'])
                    
                    if len(celdas) < 8:  # Necesitamos al menos 8 celdas para incluir minutos
                        continue
                    
                    # Extraer temporada
                    temporada = celdas[0].text.strip()
                    
                    # Extraer competición
                    competicion = celdas[2].text.strip()
                    
                    # Extraer partidos jugados (celda 3)
                    partidos_texto = celdas[3].text.strip()
                    partidos = self._convertir_a_numero(partidos_texto)
                    
                    # Extraer goles (celda 4)
                    goles_texto = celdas[4].text.strip()
                    goles = self._convertir_a_numero(goles_texto)
                    
                    # Extraer tarjetas (celda 6)
                    tarjetas_texto = celdas[6].text.strip()
                    amarillas, doble_amarillas, rojas = self._parsear_tarjetas(tarjetas_texto)
                    
                    # Extraer minutos jugados (celda 7)
                    minutos_texto = celdas[7].text.strip()
                    minutos = self._extraer_minutos(minutos_texto)
                    
                    # Solo agregar si hay alguna estadística relevante
                    if partidos > 0 or goles > 0 or minutos > 0 or amarillas > 0 or doble_amarillas > 0 or rojas > 0:
                        stats_list.append({
                            'temporada': temporada,
                            'competicion': competicion,
                            'partidos': partidos,
                            'goles': goles,
                            'minutos': minutos,
                            'amarillas': amarillas,
                            'doble_amarillas': doble_amarillas,
                            'rojas': rojas
                        })
                
                except Exception:
                    continue
            
            return stats_list
        
        except Exception as e:
            print(f"      ⚠️  Error obteniendo estadísticas: {e}")
            return []