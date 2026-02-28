"""
Servicio para extraer jugadores dirigidos por un técnico.
"""

import re
from typing import List, Dict, Tuple, Optional
from bs4 import BeautifulSoup

from ..config import Settings
from ..utils import HTTPClient
from ..models import JugadorBajoTecnico, JugadoresPorTorneo


class TecnicoJugadoresService:
    """Servicio para extraer jugadores dirigidos por un técnico en Rosario Central."""
    
    def __init__(self, settings: Optional[Settings] = None, http_client: Optional[HTTPClient] = None):
        self.settings = settings or Settings()
        self.http_client = http_client or HTTPClient(self.settings)
        self.base_url = self.settings.TRANSFERMARKT_BASE_URL
        self.club_id = self.settings.TRANSFERMARKT_CLUB_ID
    
    def obtener_jugadores_por_tecnico(
        self, 
        trainer_id: str, 
        nombre_tecnico: str,
        nombre_url: str
    ) -> List[JugadoresPorTorneo]:
        """
        Obtiene todos los jugadores dirigidos por un técnico en Rosario Central,
        agrupados por torneo y temporada.
        
        Args:
            trainer_id: ID del técnico en Transfermarkt
            nombre_tecnico: Nombre del técnico (para logging)
            nombre_url: Nombre del técnico en formato URL (ej: 'miguel-angel-russo')
        
        Returns:
            Lista de JugadoresPorTorneo con todos los torneos del técnico
        """
        print(f"   🔍 Extrayendo jugadores dirigidos por {nombre_tecnico}...")
        
        # Primero, obtener las temporadas en las que estuvo en Central
        temporadas = self._obtener_temporadas_en_central(trainer_id)
        
        if not temporadas:
            print(f"      ⚠️  No se encontraron temporadas para {nombre_tecnico}")
            return []
        
        print(f"      ✅ Encontradas {len(temporadas)} temporadas")
        
        # Para cada temporada, obtener los torneos y jugadores
        todos_los_torneos = []
        
        for temporada in temporadas:
            torneos = self._obtener_torneos_de_temporada(trainer_id, temporada, nombre_tecnico, nombre_url)
            todos_los_torneos.extend(torneos)
        
        print(f"      ✅ Total: {len(todos_los_torneos)} torneos con jugadores")
        
        return todos_los_torneos
    
    def _obtener_temporadas_en_central(self, trainer_id: str) -> List[str]:
        """
        Obtiene las temporadas en las que el técnico estuvo en Rosario Central.
        
        Args:
            trainer_id: ID del técnico
        
        Returns:
            Lista de años de temporadas (ej: ['2022', '2023'])
        """
        url = f"{self.base_url}/trainer/profil/trainer/{trainer_id}"
        
        try:
            response = self.http_client.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Buscar la tabla de estaciones/clubes
            temporadas = set()
            table = soup.find('table', class_='items')
            
            if not table:
                return []
            
            # Buscar todas las filas con <td>
            all_rows = table.find_all('tr')
            rows_with_td = [r for r in all_rows if r.find_all('td')]
            
            for row in rows_with_td:
                cells = row.find_all('td')
                if len(cells) < 3:
                    continue
                
                # Verificar si es Rosario Central (celda 1)
                club_cell = cells[1]
                club_text = club_cell.get_text(strip=True)
                if 'Rosario Central' not in club_text:
                    continue
                
                # Extraer la temporada (celda 2) - formato: "22/23 (01/01/2023)"
                temporada_cell = cells[2]
                temporada_text = temporada_cell.get_text(strip=True)
                
                # Extraer AMBOS años de la temporada (ej: "22/23" -> ["2022", "2023"])
                # Formato puede ser "22/23" o "24/25" o "97/98"
                match = re.search(r'(\d{2})/(\d{2})', temporada_text)
                if match:
                    año1_corto = int(match.group(1))
                    año2_corto = int(match.group(2))
                    
                    # Convertir ambos años
                    for año_corto in [año1_corto, año2_corto]:
                        # Decidir siglo: >= 50 -> 19XX, < 50 -> 20XX
                        if año_corto >= 50:
                            año_completo = f"19{año_corto}"
                        else:
                            año_completo = f"20{año_corto:02d}"
                        temporadas.add(año_completo)
            
            return sorted(list(temporadas), reverse=True)  # Más recientes primero
        
        except Exception as e:
            print(f"      ⚠️  Error obteniendo temporadas: {e}")
            return []
    
    def _obtener_torneos_de_temporada(
        self, 
        trainer_id: str, 
        temporada: str,
        nombre_tecnico: str,
        nombre_url: str
    ) -> List[JugadoresPorTorneo]:
        """
        Obtiene todos los torneos de una temporada con sus jugadores.
        
        Args:
            trainer_id: ID del técnico
            temporada: Año de la temporada (ej: '2022')
            nombre_tecnico: Nombre del técnico
            nombre_url: Nombre del técnico en formato URL (ej: 'miguel-angel-russo')
        
        Returns:
            Lista de JugadoresPorTorneo para esa temporada
        """
        # URL para obtener jugadores de una temporada específica (vista compacta)
        url = (
            f"{self.base_url}/{nombre_url}/eingesetzteSpieler/trainer/{trainer_id}/plus/0"
            f"?saison_id={temporada}&verein_id={self.club_id}"
        )
        
        try:
            response = self.http_client.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Obtener filtros de competición disponibles
            torneos_info = self._extraer_torneos_de_filtros(soup)
            
            if not torneos_info:
                # Si no hay filtros específicos, intentar con la tabla principal
                jugadores = self._extraer_jugadores_de_tabla(soup, url, False)
                if jugadores:
                    return [JugadoresPorTorneo(
                        torneo=f"Temporada {temporada}",
                        temporada=temporada,
                        total_jugadores=len(jugadores),
                        jugadores=jugadores
                    )]
                return []
            
            # Para cada torneo encontrado, obtener sus jugadores
            torneos_result = []
            
            for torneo_nombre, wettbewerb_id in torneos_info:
                # Vista compacta (plus/0) para datos básicos
                url_torneo = (
                    f"{self.base_url}/{nombre_url}/eingesetzteSpieler/trainer/{trainer_id}/plus/0"
                    f"?saison_id={temporada}&verein_id={self.club_id}&wettbewerb_id={wettbewerb_id}"
                )
                
                # Vista ampliada (plus/1) para minutos
                url_ampliada = (
                    f"{self.base_url}/{nombre_url}/eingesetzteSpieler/trainer/{trainer_id}/plus/1"
                    f"?saison_id={temporada}&verein_id={self.club_id}&wettbewerb_id={wettbewerb_id}"
                )
                
                try:
                    # Obtener datos básicos de vista compacta
                    response_torneo = self.http_client.get(url_torneo)
                    soup_torneo = BeautifulSoup(response_torneo.content, 'html.parser')
                    jugadores = self._extraer_jugadores_de_tabla(soup_torneo, url_torneo, False)
                    
                    # Obtener minutos de vista ampliada
                    if jugadores:
                        try:
                            response_ampliada = self.http_client.get(url_ampliada)
                            soup_ampliada = BeautifulSoup(response_ampliada.content, 'html.parser')
                            minutos_dict = self._extraer_minutos(soup_ampliada)
                            
                            # Actualizar minutos de cada jugador
                            for jugador in jugadores:
                                if jugador.nombre in minutos_dict:
                                    jugador.minutos = minutos_dict[jugador.nombre]
                        except Exception as e:
                            print(f"      ⚠️  Error extrayendo minutos: {e}")
                    
                    if jugadores:
                        torneos_result.append(JugadoresPorTorneo(
                            torneo=torneo_nombre,
                            temporada=temporada,
                            total_jugadores=len(jugadores),
                            jugadores=jugadores
                        ))
                except Exception as e:
                    print(f"      ⚠️  Error en {torneo_nombre} ({temporada}): {e}")
                    continue
            
            return torneos_result
        
        except Exception as e:
            print(f"      ⚠️  Error en temporada {temporada}: {e}")
            return []
    
    def _extraer_torneos_de_filtros(self, soup: BeautifulSoup) -> List[Tuple[str, str]]:
        """
        Extrae los torneos disponibles de los filtros de la página.
        
        Args:
            soup: BeautifulSoup de la página
        
        Returns:
            Lista de tuplas (nombre_torneo, wettbewerb_id)
        """
        torneos = []
        
        # Buscar el select de competiciones
        select = soup.find('select', {'name': 'wettbewerb_id'})
        
        if not select:
            return torneos
        
        options = select.find_all('option')
        
        for option in options:
            value = option.get('value', '').strip()
            text = option.get_text(strip=True)
            
            # Ignorar la opción vacía o "Todas las competiciones"
            if not value or not text or 'Todas' in text or 'Competiciones' in text:
                continue
            
            torneos.append((text, value))
        
        return torneos
    
    def _extraer_minutos(self, soup: BeautifulSoup) -> dict:
        """
        Extrae minutos jugados de la vista ampliada.
        
        Returns:
            Diccionario {nombre_jugador: minutos}
        """
        minutos_dict = {}
        
        table = soup.find('table', class_='items')
        if not table:
            return minutos_dict
        
        rows = table.find_all('tr', class_=['odd', 'even'])
        
        for row in rows:
            try:
                cells = row.find_all('td')
                
                if len(cells) < 13:
                    continue
                
                # Nombre (celda 2)
                nombre_cell = cells[2]
                nombre_link = nombre_cell.find('a', href=True)
                if not nombre_link:
                    continue
                
                nombre = nombre_link.get_text(strip=True)
                
                # Minutos (celda 12 en vista ampliada)
                minutos_text = cells[12].get_text(strip=True)
                
                # Parsear minutos (formato: "1.334'" o "1.334")
                minutos_clean = minutos_text.replace('.', '').replace(',', '').replace("'", '').strip()
                minutos_match = re.search(r'(\d+)', minutos_clean)
                
                if minutos_match:
                    minutos_dict[nombre] = int(minutos_match.group(1))
            
            except Exception as e:
                continue
        
        return minutos_dict
    
    def _extraer_jugadores_de_tabla(self, soup: BeautifulSoup, url: str, is_expanded: bool = False) -> List[JugadorBajoTecnico]:
        """
        Extrae jugadores de la tabla de apariciones.
        
        Args:
            soup: BeautifulSoup de la página
            url: URL de donde se extraen los jugadores (para debug)
        
        Returns:
            Lista de JugadorBajoTecnico
        """
        jugadores = []
        
        # Buscar tabla de jugadores
        table = soup.find('table', class_='items')
        
        if not table:
            return jugadores
        
        rows = table.find_all('tr', class_=['odd', 'even'])
        
        for row in rows:
            try:
                cells = row.find_all('td')
                
                if len(cells) < 7:
                    continue
                
                # Estructura de celdas:
                # [0]: Nombre + Posición juntos (texto)
                # [1]: Imagen del jugador
                # [2]: Nombre del jugador (con link)
                # [3]: Posición
                # [4]: Nacionalidad (imagen)
                # [5]: Apariciones ⚠️ IMPORTANTE: Esta es la celda correcta
                # [6]: Goles
                # [7]: Asistencias
                
                nombre_cell = cells[2]
                nombre_link = nombre_cell.find('a', href=True)
                
                if not nombre_link:
                    continue
                
                nombre = nombre_link.get_text(strip=True)
                url_perfil = self.base_url + nombre_link['href']
                
                # Posición (celda 3)
                posicion = cells[3].get_text(strip=True) if len(cells) > 3 else ''
                
                # Nacionalidad (celda 4, imagen)
                nacionalidad = ''
                if len(cells) > 4:
                    nacionalidad_cell = cells[4]
                    nacionalidad_img = nacionalidad_cell.find('img', {'class': 'flaggenrahmen'})
                    if nacionalidad_img:
                        nacionalidad = nacionalidad_img.get('title', '')
                
                # Apariciones (celda 5) ✅ CORREGIDO
                apariciones = 0
                if len(cells) > 5:
                    apariciones_text = cells[5].get_text(strip=True)
                    apariciones_match = re.search(r'\d+', apariciones_text)
                    if apariciones_match:
                        apariciones = int(apariciones_match.group())
                
                # Goles (celda 6) ✅ CORREGIDO
                goles = 0
                if len(cells) > 6:
                    goles_text = cells[6].get_text(strip=True)
                    goles_match = re.search(r'\d+', goles_text)
                    if goles_match:
                        goles = int(goles_match.group())
                
                # Asistencias (celda 7) ✅ CORREGIDO
                asistencias = 0
                if len(cells) > 7:
                    asistencias_text = cells[7].get_text(strip=True)
                    asistencias_match = re.search(r'\d+', asistencias_text)
                    if asistencias_match:
                        asistencias = int(asistencias_match.group())
                
                jugador = JugadorBajoTecnico(
                    nombre=nombre,
                    nacionalidad=nacionalidad,
                    posicion=posicion,
                    apariciones=apariciones,
                    goles=goles,
                    asistencias=asistencias,
                    minutos=0,  # Se actualizará desde la vista ampliada
                    url_perfil=url_perfil
                )
                
                jugadores.append(jugador)
            
            except Exception as e:
                print(f"      ⚠️  Error extrayendo jugador: {e}")
                continue
        
        return jugadores
