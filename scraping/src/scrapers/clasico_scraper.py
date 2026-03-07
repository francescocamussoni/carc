"""
Scraper para partidos clásicos Rosario Central vs Newell's Old Boys
Extrae formaciones, goles y árbitros de cada partido
"""
import re
import time
import logging
from typing import List, Optional, Dict, Tuple
from bs4 import BeautifulSoup, Tag
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock

from src.models.partido_clasico import (
    PartidoClasico,
    FormacionEquipo,
    JugadorPartido,
    Entrenador,
    Gol,
    Arbitro,
    ClasicosCollection
)

try:
    from src.utils.http_client import HTTPClient
    from src.services.image_service import ImageService
    from src.config.settings import Settings
except ImportError:
    # Fallback si no está disponible
    import requests
    
    class HTTPClient:
        def get(self, url: str):
            return requests.get(url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }, timeout=30)
    
    ImageService = None
    Settings = None


class ClasicoScraper:
    """
    Scraper para partidos clásicos Rosario Central vs Newell's Old Boys
    """
    
    BASE_URL_ENCUENTROS = "https://www.transfermarkt.com.ar/vergleich/vereineBegegnungen/statistik/1418_1286"
    BASE_URL_PARTIDO = "https://www.transfermarkt.com.ar/spielbericht/index/spielbericht/{partido_id}"
    BASE_URL_AUFSTELLUNG = "https://www.transfermarkt.com.ar/ca-newells-old-boys_ca-rosario-central/aufstellung/spielbericht/{partido_id}"
    
    def __init__(self):
        try:
            self.settings = Settings()
            self.http_client = HTTPClient(self.settings)
            self.image_service = ImageService(self.settings, self.http_client)
        except:
            # Fallback simple
            import requests
            self.settings = None
            self.http_client = type('obj', (object,), {
                'get': lambda self, url: requests.get(url, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }, timeout=30)
            })()
            self.image_service = None
        
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.partidos_scrapeados = 0
        self.partidos_con_formacion = 0
        self.delay_between_requests = 0.3  # seconds (reducido por paralelización)
        self._lock = Lock()  # Para thread-safety
        self.max_workers = 8  # Paralelización (8 threads simultáneos)
    
    def fetch_page(self, url: str) -> Optional[str]:
        """
        Obtiene el HTML de una página
        
        Args:
            url: URL a scrapear
            
        Returns:
            HTML como string o None si falla
        """
        try:
            response = self.http_client.get(url)
            if response and response.status_code == 200:
                return response.text
            else:
                self.logger.error(f"Error al obtener {url}: status {response.status_code if response else 'None'}")
                return None
        except Exception as e:
            self.logger.error(f"Excepción al obtener {url}: {e}")
            return None
    
    def delay(self):
        """Espera entre requests para evitar rate limiting"""
        time.sleep(self.delay_between_requests)
    
    def scrape_listado_partidos(self) -> List[Dict]:
        """
        Scrape la página principal con el listado de todos los encuentros
        
        Returns:
            Lista de diccionarios con información básica de cada partido
        """
        self.logger.info("Scrapeando listado de partidos clásicos...")
        
        html = self.fetch_page(self.BASE_URL_ENCUENTROS)
        if not html:
            self.logger.error("No se pudo obtener el listado de partidos")
            return []
        
        soup = BeautifulSoup(html, 'html.parser')
        partidos = []
        
        # Buscar todas las tablas y elegir la que tiene más filas (partidos)
        tablas = soup.find_all('table')
        tabla = None
        max_filas = 0
        
        for t in tablas:
            tbody = t.find('tbody')
            if tbody:
                filas_count = len(tbody.find_all('tr'))
                if filas_count > max_filas:
                    max_filas = filas_count
                    tabla = t
        
        if not tabla or max_filas == 0:
            self.logger.error("No se encontró la tabla de partidos")
            return []
        
        self.logger.info(f"Tabla encontrada con {max_filas} partidos")
        
        # Iterar sobre las filas de la tabla
        filas = tabla.find('tbody').find_all('tr')
        
        for fila in filas:
            try:
                partido_info = self._parse_fila_partido(fila)
                if partido_info:
                    partidos.append(partido_info)
            except Exception as e:
                self.logger.warning(f"Error parseando fila: {e}")
                continue
        
        self.logger.info(f"✅ Encontrados {len(partidos)} partidos en el listado")
        return partidos
    
    def _parse_fila_partido(self, fila: Tag) -> Optional[Dict]:
        """
        Parsea una fila de la tabla de partidos
        
        Args:
            fila: Tag de BeautifulSoup con la fila <tr>
            
        Returns:
            Diccionario con información básica del partido
        """
        celdas = fila.find_all('td')
        if len(celdas) < 13:
            return None
        
        try:
            # Celda 1: competición (imagen)
            competicion_img = celdas[1].find('img')
            competicion = competicion_img.get('title', 'Desconocida') if competicion_img else 'Desconocida'
            
            # Celda 2: jornada
            jornada = celdas[2].get_text(strip=True)
            
            # Celda 3: fecha
            fecha_texto = celdas[3].get_text(strip=True)
            fecha = self._parse_fecha(fecha_texto)
            
            # Celdas 5-7: equipo local (imagen, sigla, nombre completo)
            # Usamos la celda 7 que tiene el nombre completo
            local = celdas[7].find('a').get_text(strip=True) if celdas[7].find('a') else None
            
            # Celdas 8-10: equipo visitante
            # Usamos la celda 10 que tiene el nombre completo
            visitante = celdas[10].find('a').get_text(strip=True) if celdas[10].find('a') else None
            
            # Celda 12: resultado con link
            resultado_celda = celdas[12]
            resultado = None
            partido_id = None
            
            if resultado_celda:
                resultado_link = resultado_celda.find('a')
                if resultado_link:
                    resultado = resultado_link.get_text(strip=True)
                    # Extraer partido_id del href: /spielbericht/index/spielbericht/4798353
                    href = resultado_link.get('href', '')
                    match = re.search(r'/spielbericht/(\d+)', href)
                    if match:
                        partido_id = match.group(1)
            
            # Solo procesar partidos que tengan partido_id (enlace al detalle)
            if not partido_id:
                return None
            
            # Determinar si Rosario Central jugó de local
            rosario_central_local = 'Rosario Central' in local if local else False
            
            return {
                'partido_id': partido_id,
                'fecha': fecha,
                'competicion': competicion,
                'jornada': jornada,
                'local': local,
                'visitante': visitante,
                'resultado': resultado,
                'rosario_central_local': rosario_central_local
            }
        
        except Exception as e:
            self.logger.warning(f"Error parseando fila: {e}")
            return None
    
    def _parse_fecha(self, fecha_texto: str) -> str:
        """
        Convierte fecha de formato español a ISO (YYYY-MM-DD)
        
        Ejemplos:
            "sáb, 15/02/2025" -> "2025-02-15"
            "vie, 22/08/2025" -> "2025-08-22"
        """
        try:
            # Extraer solo la parte de la fecha DD/MM/YYYY
            match = re.search(r'(\d{2})/(\d{2})/(\d{4})', fecha_texto)
            if match:
                dia, mes, anio = match.groups()
                return f"{anio}-{mes}-{dia}"
        except:
            pass
        
        return fecha_texto
    
    def scrape_detalle_partido(self, partido_id: str) -> Optional[PartidoClasico]:
        """
        Scrape el detalle completo de un partido (formación, goles, árbitro)
        
        Args:
            partido_id: ID del partido en Transfermarkt
            
        Returns:
            Objeto PartidoClasico con toda la información
        """
        url = self.BASE_URL_PARTIDO.format(partido_id=partido_id)
        self.logger.info(f"Scrapeando partido {partido_id}...")
        
        html = self.fetch_page(url)
        if not html:
            self.logger.error(f"No se pudo obtener el partido {partido_id}")
            return None
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # Extraer información básica del header
        partido_info = self._extract_partido_header(soup, partido_id, url)
        if not partido_info:
            return None
        
        # Extraer árbitro
        arbitro = self._extract_arbitro(soup)
        partido_info['arbitro'] = arbitro
        
        # Obtener la página de aufstellung para extraer formación con posiciones
        url_aufstellung = self.BASE_URL_AUFSTELLUNG.format(partido_id=partido_id)
        html_aufstellung = self.fetch_page(url_aufstellung)
        
        formacion = None
        if html_aufstellung:
            soup_aufstellung = BeautifulSoup(html_aufstellung, 'html.parser')
            # Pasar también el soup original para extraer el entrenador
            formacion = self._extract_formacion_rosario_central(soup_aufstellung, partido_info['rosario_central_local'], partido_id, soup)
        else:
            self.logger.warning(f"No se pudo obtener la página de aufstellung para partido {partido_id}")
        
        partido_info['formacion_rosario_central'] = formacion
        
        # Extraer goles de Rosario Central
        goles = self._extract_goles_rosario_central(soup, partido_info['rosario_central_local'])
        partido_info['goles_rosario_central'] = goles
        
        # Crear objeto PartidoClasico
        partido = PartidoClasico(**partido_info)
        
        with self._lock:
            self.partidos_scrapeados += 1
            if formacion:
                self.partidos_con_formacion += 1
        
        self.logger.info(f"✅ Partido {partido_id} scrapeado exitosamente")
        return partido
    
    def _extract_partido_header(self, soup: BeautifulSoup, partido_id: str, url: str) -> Optional[Dict]:
        """Extrae información básica del header del partido"""
        try:
            # Extraer equipos del H1
            h1 = soup.find('h1')
            if not h1:
                return None
            
            h1_text = h1.get_text(strip=True)
            # El H1 tiene formato "Newell's - Rosario Central"
            if ' - ' not in h1_text:
                return None
            
            partes = h1_text.split(' - ')
            if len(partes) != 2:
                return None
            
            local = partes[0].strip()
            visitante = partes[1].strip()
            
            # Expandir nombres abreviados
            if local == "Newell's":
                local = "Newell's Old Boys"
            if visitante == "Newell's":
                visitante = "Newell's Old Boys"
            
            # Extraer resultado
            resultado_div = soup.find('div', class_='sb-endstand')
            resultado = resultado_div.get_text(strip=True) if resultado_div else None
            
            # Calcular goles (limpiar resultado parcial entre paréntesis)
            goles_local, goles_visitante = 0, 0
            if resultado and ':' in resultado:
                # Remover el resultado del medio tiempo: "0:2(0:0)" -> "0:2"
                resultado_limpio = resultado.split('(')[0].strip()
                partes = resultado_limpio.split(':')
                goles_local = int(partes[0].strip())
                goles_visitante = int(partes[1].strip())
            
            # Extraer fecha y competición
            datum_box = soup.find('p', class_='sb-datum')
            fecha = None
            competicion = "Desconocida"
            jornada = ""
            
            if datum_box:
                # Fecha
                fecha_texto = datum_box.get_text(strip=True)
                fecha = self._parse_fecha_detalle(fecha_texto)
                
                # Competición (buscar en el link)
                comp_link = datum_box.find('a')
                if comp_link:
                    competicion = comp_link.get_text(strip=True)
            
            # Extraer estadio y espectadores
            estadio = None
            espectadores = None
            
            estadio_box = soup.find('p', class_='sb-zusatzinfos')
            if estadio_box:
                texto = estadio_box.get_text()
                # Buscar estadio
                if 'Estadio:' in texto:
                    estadio_match = re.search(r'Estadio:\s*([^|]+)', texto)
                    if estadio_match:
                        estadio = estadio_match.group(1).strip()
                
                # Buscar espectadores
                if 'Espectadores:' in texto or 'spectadores' in texto.lower():
                    esp_match = re.search(r'(\d+\.?\d*)\s*Espectadores', texto, re.IGNORECASE)
                    if esp_match:
                        espectadores = esp_match.group(1)
            
            # Determinar si Rosario Central jugó de local
            rosario_central_local = 'Rosario Central' in local if local else False
            
            return {
                'partido_id': partido_id,
                'fecha': fecha,
                'competicion': competicion,
                'jornada': jornada,
                'local': local,
                'visitante': visitante,
                'resultado': resultado,
                'goles_local': goles_local,
                'goles_visitante': goles_visitante,
                'estadio': estadio,
                'espectadores': espectadores,
                'rosario_central_local': rosario_central_local,
                'url_partido': url
            }
        
        except Exception as e:
            self.logger.error(f"Error extrayendo header: {e}")
            return None
    
    def _parse_fecha_detalle(self, fecha_texto: str) -> str:
        """
        Parsea fecha del detalle del partido
        Ejemplo: "sábado, 15/02/2025 20:30h" -> "2025-02-15"
        """
        try:
            match = re.search(r'(\d{2})/(\d{2})/(\d{4})', fecha_texto)
            if match:
                dia, mes, anio = match.groups()
                return f"{anio}-{mes}-{dia}"
        except:
            pass
        
        return fecha_texto
    
    def _extract_arbitro(self, soup: BeautifulSoup) -> Optional[Arbitro]:
        """Extrae información del árbitro"""
        try:
            # Buscar el texto "Árbitro:" en la página
            arbitro_text = soup.find(string=lambda t: t and 'Árbitro' in t)
            if not arbitro_text:
                return None
            
            parent = arbitro_text.find_parent('div')
            if not parent:
                return None
            
            # Buscar link del árbitro
            arbitro_link = parent.find('a', href=lambda h: h and '/schiedsrichter/' in h)
            if not arbitro_link:
                return None
            
            nombre_completo = arbitro_link.get_text(strip=True)
            
            # Separar nombre y apellido
            partes = nombre_completo.split()
            apellido = partes[-1] if partes else nombre_completo
            nombre = ' '.join(partes[:-1]) if len(partes) > 1 else ""
            
            # Extraer foto
            foto_url = None
            foto_img = parent.find('img')
            if foto_img:
                foto_url = foto_img.get('src')
            
            # Extraer nacionalidad (si está disponible)
            nacionalidad = None
            flag_img = parent.find('img', class_='flaggenrahmen')
            if flag_img:
                nacionalidad = flag_img.get('title')
            
            return Arbitro(
                nombre=nombre,
                apellido=apellido,
                nombre_completo=nombre_completo,
                nacionalidad=nacionalidad,
                foto_url=foto_url
            )
        
        except Exception as e:
            self.logger.warning(f"Error extrayendo árbitro: {e}")
            return None
    
    def _extract_formacion_rosario_central(
        self, 
        soup: BeautifulSoup, 
        rosario_central_local: bool,
        partido_id: str,
        soup_original: Optional[BeautifulSoup] = None
    ) -> Optional[FormacionEquipo]:
        """
        Extrae la formación de Rosario Central desde la página de AUFSTELLUNG
        Tiene las posiciones explícitas y separa claramente titulares de suplentes
        
        Args:
            soup: BeautifulSoup del HTML de la página aufstellung
            rosario_central_local: True si RC jugó de local
            partido_id: ID del partido
            soup_original: BeautifulSoup del HTML de la página normal del partido (para extraer entrenador)
        """
        try:
            import re
            
            # 1. Buscar los divs "large-6 columns" que contienen las formaciones
            large_6_divs = soup.find_all('div', class_=lambda x: x and 'large-6' in x and 'columns' in x)
            
            if len(large_6_divs) < 2:
                self.logger.warning(f"Solo se encontraron {len(large_6_divs)} divs large-6")
                return None
            
            # Seleccionar el div correcto (0=local, 1=visitante)
            rc_div = large_6_divs[0] if rosario_central_local else large_6_divs[1]
            
            # 2. Buscar el box dentro del div
            rc_box = rc_div.find('div', class_='box')
            if not rc_box:
                self.logger.warning("No se encontró el box de formación")
                return None
            
            # 3. EXTRAER EL ESQUEMA TÁCTICO
            # El esquema está en la página PRINCIPAL del partido (soup_original), NO en aufstellung
            # Ejemplo: <div class="large-7 aufstellung-vereinsseite columns small-12 unterueberschrift formation-subtitle">
            #            Starting Line-up: 3-5-2 Attacking
            #          </div>
            esquema = "4-3-3"  # Default fallback
            
            if soup_original:
                # Buscar divs con clase "formation-subtitle" en la página principal
                formation_divs = soup_original.find_all('div', class_='formation-subtitle')
                
                esquemas_found = []
                for div in formation_divs:
                    text = div.get_text(strip=True)
                    # Buscar patrón de esquema (ej: "3-5-2", "4-2-3-1")
                    if 'Starting Line-up' in text or 'Formación inicial' in text:
                        match = re.search(r'(\d+-\d+-\d+(?:-\d+)?)', text)
                        if match:
                            esquemas_found.append((match.group(1), text))
                
                self.logger.info(f"🔍 Encontrados {len(esquemas_found)} esquemas en la página principal")
                
                # Si encontramos esquemas, tomar el que corresponde (0=local, 1=visitante)
                if len(esquemas_found) >= 2:
                    idx = 0 if rosario_central_local else 1
                    esquema = esquemas_found[idx][0]
                    self.logger.info(f"✅ Esquema detectado: {esquema} (RC {'local' if rosario_central_local else 'visitante'})")
                elif len(esquemas_found) == 1:
                    esquema = esquemas_found[0][0]
                    self.logger.info(f"✅ Esquema detectado (único): {esquema}")
                else:
                    self.logger.warning(f"⚠️  No se encontró esquema, usando default: {esquema}")
            else:
                self.logger.warning(f"⚠️  soup_original no disponible, usando esquema default: {esquema}")
            
            # 4. EXTRAER JUGADORES TITULARES Y POSICIONES desde las tablas
            tablas = rc_box.find_all('table')
            self.logger.info(f"Encontradas {len(tablas)} tablas en el box de RC")
            
            jugadores_data = []
            entrenador_data = None
            
            # Iterar sobre las tablas para encontrar jugadores
            for tabla in tablas:
                filas = tabla.find_all('tr')
                
                for fila in filas:
                    celdas = fila.find_all('td')
                    
                    # Los jugadores están en filas con exactamente 6 celdas
                    if len(celdas) != 6:
                        # Verificar si es el entrenador (en tabla diferente)
                        if 'Entrenador' in fila.get_text() or 'Coach' in fila.get_text() or 'Trainer' in fila.get_text():
                            entrenador_link = fila.find('a', href=lambda x: x and '/profil/trainer/' in str(x))
                            if entrenador_link and not entrenador_data:
                                nombre_completo = entrenador_link.get_text(strip=True)
                                trainer_url = entrenador_link.get('href', '')
                                
                                trainer_id = None
                                id_match = re.search(r'/trainer/(\d+)', trainer_url)
                                if id_match:
                                    trainer_id = id_match.group(1)
                                
                                # Descargar imagen localmente
                                image_url = None
                                if trainer_id and self.image_service:
                                    tm_image_url = f"https://img.a.transfermarkt.technology/portrait/medium/{trainer_id}-0.jpg"
                                    image_url = self.image_service.descargar_imagen(tm_image_url, nombre_completo)
                                    if image_url:
                                        self.logger.info(f"      📷 Imagen DT guardada: {image_url}")
                                
                                entrenador_data = {
                                    'nombre_completo': nombre_completo,
                                    'image_url': image_url
                                }
                        continue
                    
                    # Primera celda: número
                    numero_text = celdas[0].get_text(strip=True)
                    
                    # Si no tiene número, no es un jugador titular
                    if not numero_text.isdigit():
                        continue
                    
                    numero = int(numero_text)
                    
                    # El nombre del jugador está en la celda 3
                    # El link está dentro de la celda 3
                    jugador_link = celdas[3].find('a', href=lambda x: x and '/spieler/' in str(x))
                    
                    if not jugador_link:
                        continue
                    
                    nombre_completo = jugador_link.get_text(strip=True)
                    # Limpiar el nombre (puede incluir edad)
                    nombre_completo = re.sub(r'\(\d+\s+[Aa]ños?\)', '', nombre_completo).strip()
                    
                    jugador_url = jugador_link.get('href', '')
                    
                    # Extraer ID del jugador
                    jugador_id = None
                    id_match = re.search(r'/spieler/(\d+)', jugador_url)
                    if id_match:
                        jugador_id = id_match.group(1)
                    
                    # Descargar imagen localmente
                    image_url = None
                    if jugador_id and self.image_service:
                        tm_image_url = f"https://img.a.transfermarkt.technology/portrait/medium/{jugador_id}-0.jpg"
                        image_url = self.image_service.descargar_imagen(tm_image_url, nombre_completo)
                        if image_url:
                            self.logger.info(f"      📷 Imagen guardada: {image_url}")
                        else:
                            self.logger.warning(f"      ⚠️  No se pudo descargar imagen para {nombre_completo}")
                    
                    # Extraer posición (celda 4 contiene "Posición, Valor")
                    posicion_tm = None
                    posicion_text = celdas[4].get_text(strip=True)
                    # Formato: "Portero, 125 mil €" -> extraer "Portero"
                    if ',' in posicion_text:
                        posicion_tm = posicion_text.split(',')[0].strip()
                    else:
                        posicion_tm = posicion_text
                    
                    if posicion_tm and nombre_completo:
                        jugadores_data.append({
                            'numero': numero,
                            'nombre_completo': nombre_completo,
                            'jugador_id': jugador_id,
                            'image_url': image_url,
                            'posicion_tm': posicion_tm
                        })
                    
                    # Si ya tenemos 11 jugadores, detener
                    if len(jugadores_data) >= 11:
                        break
                
                # Si ya tenemos 11 jugadores, salir del bucle de tablas
                if len(jugadores_data) >= 11:
                    break
            
            if len(jugadores_data) != 11:
                self.logger.warning(f"Se esperaban 11 titulares, se encontraron {len(jugadores_data)}")
                return None
            
            # 5. CREAR OBJETOS JUGADOR
            jugadores_titulares = []
            for jdata in jugadores_data:
                nombre_completo = jdata['nombre_completo']
                
                # Parsear nombre
                partes = nombre_completo.split()
                apellido = partes[-1] if partes else nombre_completo
                nombre = ' '.join(partes[:-1]) if len(partes) > 1 else ""
                
                # Normalizar posición
                posicion = self._normalize_position(jdata.get('posicion_tm', 'MC'))
                
                jugador = JugadorPartido(
                    numero=jdata['numero'],
                    nombre=nombre,
                    apellido=apellido,
                    nombre_completo=nombre_completo,
                    posicion=posicion,
                    titular=True,
                    foto_url=jdata['image_url']
                )
                
                jugadores_titulares.append(jugador)
            
            # 6. EXTRAER ENTRENADOR desde la página original del partido
            entrenador = None
            if soup_original:
                # Buscar la tabla de formación en la página original
                h2_formacion = None
                for h2 in soup_original.find_all('h2'):
                    if 'Formación' in h2.get_text():
                        h2_formacion = h2
                        break
                
                if h2_formacion:
                    parent = h2_formacion.find_parent('div', class_='box')
                    if parent:
                        # Buscar las tablas de formación
                        tablas = parent.find_all('table')
                        if len(tablas) >= 2:
                            # Seleccionar la tabla correcta (0=local, 1=visitante)
                            tabla_rc = tablas[0] if rosario_central_local else tablas[1]
                            
                            # Buscar el entrenador en la tabla
                            for tr in tabla_rc.find_all('tr'):
                                td_text = tr.get_text(strip=True)
                                if 'Entrenador' in td_text:
                                    # Buscar el link del entrenador
                                    entrenador_link = tr.find('a', href=lambda x: x and '/profil/trainer/' in str(x))
                                    if entrenador_link:
                                        nombre_completo = entrenador_link.get_text(strip=True).replace('Entrenador:', '').strip()
                                        trainer_url = entrenador_link.get('href', '')
                                        
                                        trainer_id = None
                                        id_match = re.search(r'/trainer/(\d+)', trainer_url)
                                        if id_match:
                                            trainer_id = id_match.group(1)
                                        
                                        # Descargar imagen localmente
                                        image_url = None
                                        if trainer_id and self.image_service:
                                            tm_image_url = f"https://img.a.transfermarkt.technology/portrait/medium/{trainer_id}-0.jpg"
                                            image_url = self.image_service.descargar_imagen(tm_image_url, nombre_completo)
                                            if image_url:
                                                self.logger.info(f"      📷 Imagen DT guardada: {image_url}")
                                        
                                        partes = nombre_completo.split()
                                        apellido = partes[-1] if partes else nombre_completo
                                        nombre = ' '.join(partes[:-1]) if len(partes) > 1 else ""
                                        
                                        entrenador = Entrenador(
                                            nombre=nombre,
                                            apellido=apellido,
                                            nombre_completo=nombre_completo,
                                            foto_url=image_url
                                        )
                                        break
            
            if not entrenador:
                self.logger.warning("No se pudo extraer el entrenador")
                return None
            
            # 7. ASIGNAR POSICIONES según el esquema
            jugadores_titulares = self._assign_positions_by_formation(esquema, jugadores_titulares)
            
            return FormacionEquipo(
                esquema=esquema,
                entrenador=entrenador,
                jugadores_titulares=jugadores_titulares,
                jugadores_suplentes=[]
            )
        
        except Exception as e:
            self.logger.error(f"Error extrayendo formación: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            return None
    
    def _normalize_position(self, posicion_texto: str) -> str:
        """
        Normaliza la posición del jugador a formato estándar
        
        Ejemplos:
            "POR" -> "PO"
            "Portero" -> "PO"
            "Defensa central" -> "DC"
            "Delantero" -> "DEL"
        """
        pos = posicion_texto.upper().strip()
        
        # Mapeo de posiciones
        mapeo = {
            'POR': 'PO',
            'PORTERO': 'PO',
            'DEF': 'DC',
            'DEFENSA': 'DC',
            'LATERAL': 'ED',
            'CEN': 'MC',
            'CENTRO': 'MC',
            'MEDIO': 'MC',
            'MC': 'MC',
            'MCO': 'MO',
            'LI': 'MI',
            'PIV': 'MC',
            'PIVOTE': 'MC',
            'EI': 'EI',
            'ED': 'ED',
            'DEL': 'DEL',
            'DELANTERO': 'DEL'
        }
        
        # Buscar coincidencia parcial
        for clave, valor in mapeo.items():
            if clave in pos:
                return valor
        
        return 'MC'  # Default
    
    def _assign_positions_by_formation(self, esquema: str, jugadores: List[JugadorPartido]) -> List[JugadorPartido]:
        """
        Asigna posiciones correctas según el esquema táctico y el orden de los jugadores
        Los jugadores vienen en orden de formación desde portero hasta delanteros
        
        Args:
            esquema: Esquema táctico (ej: "4-3-3", "4-4-2", "4-2-3-1")
            jugadores: Lista de 11 jugadores titulares en orden
            
        Returns:
            Lista de jugadores con posiciones correctamente asignadas
        """
        if len(jugadores) != 11:
            self.logger.warning(f"Se esperaban 11 jugadores, se recibieron {len(jugadores)}")
            return jugadores
        
        # Parse el esquema (ej: "4-3-3" -> [4, 3, 3], "4-2-3-1" -> [4, 2, 3, 1])
        try:
            lineas = [int(x) for x in esquema.split('-')]
        except:
            self.logger.warning(f"Esquema inválido: {esquema}")
            return jugadores
        
        # El primer jugador siempre es el portero
        jugadores[0].posicion = 'PO'
        idx = 1
        
        # Línea defensiva
        if len(lineas) >= 1:
            num_defensores = lineas[0]
        if num_defensores == 4:
            # 4 defensores: EI, DC, DC, ED
            jugadores[idx].posicion = 'EI'
            jugadores[idx + 1].posicion = 'DC'
            jugadores[idx + 2].posicion = 'DC'
            jugadores[idx + 3].posicion = 'ED'
        elif num_defensores == 3:
            # 3 defensores: DC, DC, DC (o EI, DC, ED para 3-5-2)
            jugadores[idx].posicion = 'DC'
            jugadores[idx + 1].posicion = 'DC'
            jugadores[idx + 2].posicion = 'DC'
        elif num_defensores == 5:
            # 5 defensores: EI, DC, DC, DC, ED
            jugadores[idx].posicion = 'EI'
            jugadores[idx + 1].posicion = 'DC'
            jugadores[idx + 2].posicion = 'DC'
            jugadores[idx + 3].posicion = 'DC'
            jugadores[idx + 4].posicion = 'ED'
        idx += num_defensores
        
        # Detectar si es formación de 3 o 4 líneas (sin contar portero)
        num_lineas = len(lineas)
        
        if num_lineas == 4:
            # Formación con 4 líneas (ej: 4-2-3-1, 4-1-4-1)
            # Línea 2: Pivotes/Mediocampistas defensivos
            num_pivotes = lineas[1]
            for i in range(num_pivotes):
                jugadores[idx + i].posicion = 'MC'
            idx += num_pivotes
            
            # Línea 3: Mediocampistas ofensivos/extremos
            num_medio_ofensivos = lineas[2]
            if num_medio_ofensivos == 3:
                # 3 mediapuntas: MI, MO, MD
                jugadores[idx].posicion = 'MI'
                jugadores[idx + 1].posicion = 'MO'
                jugadores[idx + 2].posicion = 'MD'
            elif num_medio_ofensivos == 4:
                # 4 mediapuntas: MI, MO, MO, MD
                jugadores[idx].posicion = 'MI'
                jugadores[idx + 1].posicion = 'MO'
                jugadores[idx + 2].posicion = 'MO'
                jugadores[idx + 3].posicion = 'MD'
            elif num_medio_ofensivos == 2:
                # 2 mediapuntas: MO, MO
                jugadores[idx].posicion = 'MO'
                jugadores[idx + 1].posicion = 'MO'
            elif num_medio_ofensivos == 1:
                # 1 mediapunta: MO
                jugadores[idx].posicion = 'MO'
            idx += num_medio_ofensivos
            
            # Línea 4: Delanteros
            num_delanteros = lineas[3]
            for i in range(num_delanteros):
                jugadores[idx + i].posicion = 'DEL'
        
        else:
            # Formación con 3 líneas (ej: 4-3-3, 4-4-2, 3-5-2)
            # Línea media
            if len(lineas) >= 2:
                num_medios = lineas[1]
                if num_medios == 3:
                    # 3 medios: MI, MC, MD
                    jugadores[idx].posicion = 'MI'
                    jugadores[idx + 1].posicion = 'MC'
                    jugadores[idx + 2].posicion = 'MD'
                elif num_medios == 4:
                    # 4 medios: MI, MC, MC, MD
                    jugadores[idx].posicion = 'MI'
                    jugadores[idx + 1].posicion = 'MC'
                    jugadores[idx + 2].posicion = 'MC'
                    jugadores[idx + 3].posicion = 'MD'
                elif num_medios == 2:
                    # 2 medios: MC, MC
                    jugadores[idx].posicion = 'MC'
                    jugadores[idx + 1].posicion = 'MC'
                elif num_medios == 5:
                    # 5 medios: MI, MC, MC, MC, MD
                    jugadores[idx].posicion = 'MI'
                    jugadores[idx + 1].posicion = 'MC'
                    jugadores[idx + 2].posicion = 'MC'
                    jugadores[idx + 3].posicion = 'MC'
                    jugadores[idx + 4].posicion = 'MD'
                idx += num_medios
            
            # Línea delantera
            if len(lineas) >= 3:
                num_delanteros = lineas[2]
                if num_delanteros == 3:
                    # 3 delanteros: DEL, DEL, DEL (todos delanteros)
                    jugadores[idx].posicion = 'DEL'
                    jugadores[idx + 1].posicion = 'DEL'
                    jugadores[idx + 2].posicion = 'DEL'
                elif num_delanteros == 2:
                    # 2 delanteros: DEL, DEL
                    jugadores[idx].posicion = 'DEL'
                    jugadores[idx + 1].posicion = 'DEL'
                elif num_delanteros == 1:
                    # 1 delantero: DEL
                    jugadores[idx].posicion = 'DEL'
                elif num_delanteros == 4:
                    # 4 delanteros: DEL, DEL, DEL, DEL
                    jugadores[idx].posicion = 'DEL'
                    jugadores[idx + 1].posicion = 'DEL'
                    jugadores[idx + 2].posicion = 'DEL'
                    jugadores[idx + 3].posicion = 'DEL'
        
        return jugadores
    
    def _extract_goles_rosario_central(
        self, 
        soup: BeautifulSoup, 
        rosario_central_local: bool
    ) -> List[Gol]:
        """Extrae los goles marcados por Rosario Central"""
        goles = []
        
        try:
            # Buscar la sección de Goles por H2
            h2_goles = None
            for h2 in soup.find_all('h2'):
                if 'Goles' in h2.get_text():
                    h2_goles = h2
                    break
            
            if not h2_goles:
                return []
            
            parent = h2_goles.find_parent('div', class_='box')
            if not parent:
                return []
            
            # Buscar todos los eventos de gol
            eventos = parent.find_all('div', class_='sb-aktion')
            
            for evento in eventos:
                try:
                    # Extraer resultado parcial
                    resultado_div = evento.find('div', class_='sb-aktion-spielstand')
                    resultado = resultado_div.get_text(strip=True) if resultado_div else "?"
                    
                    # Buscar jugador en el evento
                    # Buscar todos los links con jugador (pueden tener /profil/spieler/ o /leistungsdatendetails/spieler/)
                    all_links = evento.find_all('a', href=lambda h: h and '/spieler/' in h)
                    
                    # Filtrar solo links con texto (no vacíos)
                    jugador_links = [link for link in all_links if link.get_text(strip=True)]
                    
                    if not jugador_links:
                        continue
                    
                    # El primer link con texto es el goleador
                    jugador_link = jugador_links[0]
                    nombre_completo = jugador_link.get_text(strip=True)
                    
                    # Extraer minuto del texto (no del sprite)
                    texto_evento = evento.get_text()
                    minuto_match = re.search(r"(\d+)'", texto_evento)
                    minuto = minuto_match.group(1) if minuto_match else "?"
                    
                    # Parsear nombre
                    partes = nombre_completo.split()
                    apellido = partes[-1] if partes else nombre_completo
                    nombre = ' '.join(partes[:-1]) if len(partes) > 1 else ""
                    
                    # Buscar asistencia
                    asistencia_apellido = None
                    asistencia_nombre = None
                    asistencia_nombre_completo = None
                    
                    if 'asistente' in texto_evento.lower() and len(jugador_links) > 1:
                        asistente_link = jugador_links[1]
                        asistente_nombre_completo = asistente_link.get_text(strip=True)
                        asistente_partes = asistente_nombre_completo.split()
                        asistencia_apellido = asistente_partes[-1] if asistente_partes else ""
                        asistencia_nombre = ' '.join(asistente_partes[:-1]) if len(asistente_partes) > 1 else ""
                        asistencia_nombre_completo = asistente_nombre_completo
                    
                    # Determinar tipo de gol
                    tipo = "gol"
                    if 'penal' in texto_evento.lower() or 'penalty' in texto_evento.lower():
                        tipo = "penal"
                    elif 'autogol' in texto_evento.lower() or 'own goal' in texto_evento.lower():
                        tipo = "autogol"
                    
                    gol = Gol(
                        minuto=minuto,
                        jugador_nombre=nombre,
                        jugador_apellido=apellido,
                        jugador_nombre_completo=nombre_completo,
                        asistencia_nombre=asistencia_nombre,
                        asistencia_apellido=asistencia_apellido,
                        asistencia_nombre_completo=asistencia_nombre_completo,
                        tipo=tipo
                    )
                    
                    goles.append(gol)
                
                except Exception as e:
                    self.logger.warning(f"Error parseando gol: {e}")
                    continue
        
        except Exception as e:
            self.logger.error(f"Error extrayendo goles: {e}")
        
        return goles
    
    def scrape_all_clasicos(self, limite: Optional[int] = None) -> ClasicosCollection:
        """
        Scrape todos los partidos clásicos
        
        Args:
            limite: Límite opcional de partidos a scrapear
            
        Returns:
            ClasicosCollection con todos los partidos
        """
        self.logger.info("🔵⚪ Iniciando scraping de partidos clásicos Rosario Central vs Newell's")
        
        # 1. Obtener listado de partidos
        partidos_basicos = self.scrape_listado_partidos()
        
        if not partidos_basicos:
            self.logger.error("No se pudieron obtener partidos")
            return ClasicosCollection()
        
        # Aplicar límite si se especificó
        if limite:
            partidos_basicos = partidos_basicos[:limite]
            self.logger.info(f"Limitando a {limite} partidos")
        
        # 2. Scrapear detalle de cada partido (PARALELIZADO)
        collection = ClasicosCollection()
        
        def scrape_partido_wrapper(partido_info: Dict, index: int) -> Optional[PartidoClasico]:
            """Wrapper para scraping paralelo con manejo de errores"""
            partido_id = partido_info['partido_id']
            self.logger.info(f"\n[{index}/{len(partidos_basicos)}] Procesando partido {partido_id}...")
            
            try:
                partido = self.scrape_detalle_partido(partido_id)
                if partido:
                    return partido
            except Exception as e:
                self.logger.error(f"Error scrapeando partido {partido_id}: {e}")
            
            return None
        
        # Usar ThreadPoolExecutor para paralelizar
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Enviar todos los trabajos
            future_to_partido = {
                executor.submit(scrape_partido_wrapper, partido_info, i): partido_info
                for i, partido_info in enumerate(partidos_basicos, 1)
            }
            
            # Recoger resultados conforme se completan
            for future in as_completed(future_to_partido):
                try:
                    partido = future.result()
                    if partido:
                        with self._lock:
                            collection.add_partido(partido)
                except Exception as e:
                    self.logger.error(f"Error procesando resultado: {e}")
        
        # Actualizar fecha
        collection.ultima_actualizacion = datetime.now().isoformat()
        
        # Resumen
        self.logger.info(f"\n✅ Scraping completado:")
        self.logger.info(f"   Total partidos: {len(collection.partidos)}")
        self.logger.info(f"   Con formación: {self.partidos_con_formacion}")
        self.logger.info(f"   Total goles RC: {sum(len(p.goles_rosario_central) for p in collection.partidos)}")
        
        return collection
