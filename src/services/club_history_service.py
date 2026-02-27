"""
Servicio para extraer historia de clubes de jugadores desde Transfermarkt
"""

from typing import List, Dict, Optional
from bs4 import BeautifulSoup
from ..config import Settings
from ..utils import HTTPClient


class ClubHistoryService:
    """
    Servicio para obtener la historia de clubes de un jugador desde su perfil de Transfermarkt
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
    
    def obtener_clubes_jugador(self, url_perfil: str, nombre_jugador: str) -> List[Dict]:
        """
        Obtiene la lista de clubes donde jugó el jugador usando la API de Transfermarkt
        
        Args:
            url_perfil: URL del perfil del jugador (ej: /jugador/profil/spieler/12345)
            nombre_jugador: Nombre del jugador (para logging)
        
        Returns:
            Lista de diccionarios con {nombre, pais, periodo}
        """
        try:
            # MÉTODO 1 (MEJOR): Usar la API de transferHistory que devuelve JSON
            import re
            match = re.search(r'/spieler/(\d+)', url_perfil)
            if match:
                spieler_id = match.group(1)
                clubes = self._extraer_desde_api_transfers(spieler_id)
                if clubes:
                    return clubes
            
            # MÉTODO 2 (FALLBACK): Intentar desde la página de estadísticas por club
            url_stats = url_perfil.replace('/profil/', '/leistungsdatenverein/')
            clubes = self._extraer_desde_stats_por_club(url_stats)
            
            if clubes:
                return clubes
            
            # MÉTODO 3: Si no funciona, intentar desde el perfil principal
            clubes = self._extraer_desde_perfil(url_perfil)
            
            return clubes
        
        except Exception as e:
            print(f"      ⚠️  Error obteniendo clubes: {e}")
            return []
    
    def _extraer_desde_api_transfers(self, spieler_id: str) -> List[Dict]:
        """
        Extrae clubes desde la API JSON de transferHistory de Transfermarkt
        
        Args:
            spieler_id: ID del jugador en Transfermarkt
        
        Returns:
            Lista de clubes con país y período
        """
        try:
            import json
            import re
            from datetime import datetime
            
            url_api = f"{self.settings.TRANSFERMARKT_BASE_URL}/ceapi/transferHistory/list/{spieler_id}"
            response = self.http_client.get(url_api)
            
            if response.status_code != 200:
                return []
            
            data = response.json()
            
            if not data or 'transfers' not in data:
                return []
            
            clubes = []
            clubes_vistos = set()
            
            # Procesar cada transferencia
            for transfer in data.get('transfers', []):
                # Extraer info del club origen ("from")
                from_club = transfer.get('from', {})
                if from_club and not from_club.get('isSpecial', True):
                    nombre = from_club.get('clubName', '').strip()
                    if nombre and self._es_club_valido(nombre) and nombre not in clubes_vistos:
                        clubes_vistos.add(nombre)
                        
                        # Obtener país desde countryFlag o desde la página del club
                        pais = from_club.get('countryName', '')
                        if not pais or pais == '':
                            # Intentar extraer desde la URL del club
                            club_href = from_club.get('href', '')
                            pais = self._obtener_pais_del_club(club_href) if club_href else 'Desconocido'
                        
                        clubes.append({
                            'nombre': nombre,
                            'pais': pais,
                            'periodo': transfer.get('date', None)
                        })
                
                # Extraer info del club destino ("to")
                to_club = transfer.get('to', {})
                if to_club and not to_club.get('isSpecial', True):
                    nombre = to_club.get('clubName', '').strip()
                    if nombre and self._es_club_valido(nombre) and nombre not in clubes_vistos:
                        clubes_vistos.add(nombre)
                        
                        # Obtener país desde countryFlag o desde la página del club
                        pais = to_club.get('countryName', '')
                        if not pais or pais == '':
                            # Intentar extraer desde la URL del club
                            club_href = to_club.get('href', '')
                            pais = self._obtener_pais_del_club(club_href) if club_href else 'Desconocido'
                        
                        clubes.append({
                            'nombre': nombre,
                            'pais': pais,
                            'periodo': transfer.get('date', None)
                        })
            
            return clubes
        
        except Exception as e:
            # Si falla la API, silenciosamente retornar [] y dejar que los métodos fallback funcionen
            return []
    
    def _extraer_desde_stats_por_club(self, url_stats: str) -> List[Dict]:
        """
        Extrae clubes desde la página de estadísticas por club (leistungsdatenverein)
        
        Args:
            url_stats: URL de estadísticas por club
        
        Returns:
            Lista de clubes
        """
        try:
            url_completa = f"{self.settings.TRANSFERMARKT_BASE_URL}{url_stats}"
            response = self.http_client.get(url_completa)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            clubes = []
            
            # Buscar la tabla de estadísticas por club
            tablas = soup.find_all('table', class_='items')
            
            for tabla in tablas:
                filas = tabla.find_all('tr', class_=['odd', 'even'])
                
                if not filas:
                    filas = tabla.find_all('tr')[1:]  # Saltar header
                
                for fila in filas:
                    try:
                        # Buscar link del club
                        link_club = fila.find('a', href=lambda x: x and '/verein/' in x and '/spieler/' not in x)
                        
                        if not link_club:
                            continue
                        
                        # Obtener nombre del club
                        nombre_club = link_club.get('title', '').strip()
                        if not nombre_club:
                            nombre_club = link_club.text.strip()
                        
                        # Validar
                        if not self._es_club_valido(nombre_club):
                            continue
                        
                        # Evitar duplicados
                        if self._es_duplicado(nombre_club, clubes):
                            continue
                        
                        # Obtener URL del club para extraer el país
                        url_club = link_club.get('href', '')
                        pais = self._obtener_pais_del_club(url_club) if url_club else 'Desconocido'
                        
                        # Buscar temporada/período
                        # Nota: Esta página no tiene fechas, se dejará None
                        periodo = None
                        
                        clubes.append({
                            'nombre': nombre_club,
                            'pais': pais,
                            'periodo': periodo
                        })
                    
                    except Exception:
                        continue
            
            return clubes
        
        except Exception:
            return []
    
    def _obtener_pais_del_club(self, url_club: str) -> str:
        """
        Obtiene el país de un club visitando su página
        
        Args:
            url_club: URL del club (ej: /club-name/startseite/verein/1418 o /club-name/transfers/verein/1418/saison_id/2025)
        
        Returns:
            Nombre del país o 'Desconocido'
        """
        try:
            import re
            
            # Extraer el ID del club de la URL
            match = re.search(r'/verein/(\d+)', url_club)
            if not match:
                return 'Desconocido'
            
            club_id = match.group(1)
            
            # Construir URL de la página principal del club
            # Formato: /{club-slug}/startseite/verein/{id}
            # Pero como no sabemos el slug, usaremos una URL genérica que funciona
            url_completa = f"{self.settings.TRANSFERMARKT_BASE_URL}/a/startseite/verein/{club_id}"
            
            response = self.http_client.get(url_completa)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Buscar la bandera del país en el encabezado del club
            # Está en un span con clase específica
            img_bandera = soup.find('img', class_='flaggenrahmen')
            if img_bandera:
                pais = img_bandera.get('title', '').strip()
                if not pais:
                    pais = img_bandera.get('alt', '').strip()
                if pais and pais != '':
                    return pais
            
            # Buscar en meta descripción
            meta_desc = soup.find('meta', {'name': 'description'})
            if meta_desc:
                content = meta_desc.get('content', '')
                # Extraer país de patrones comunes
                paises = {
                    'Argentina': ['Argentina'],
                    'España': ['España', 'Spain'],
                    'Brasil': ['Brasil', 'Brazil'],
                    'Francia': ['Francia', 'France'],
                    'Inglaterra': ['Inglaterra', 'England'],
                    'Italia': ['Italia', 'Italy'],
                    'Alemania': ['Alemania', 'Germany', 'Deutschland'],
                    'México': ['México', 'Mexico'],
                    'Ucrania': ['Ucrania', 'Ukraine'],
                    'Uruguay': ['Uruguay'],
                    'Serbia': ['Serbia'],
                    'Portugal': ['Portugal'],
                    'Países Bajos': ['Países Bajos', 'Netherlands', 'Holanda'],
                }
                
                for pais_nombre, variantes in paises.items():
                    for variante in variantes:
                        if variante in content:
                            return pais_nombre
            
            return 'Desconocido'
        
        except Exception:
            return 'Desconocido'
    
    def _extraer_desde_transfers(self, url_transfers: str) -> List[Dict]:
        """
        Extrae clubes desde la página de transferencias
        
        Args:
            url_transfers: URL de transferencias
        
        Returns:
            Lista de clubes
        """
        try:
            url_completa = f"{self.settings.TRANSFERMARKT_BASE_URL}{url_transfers}"
            response = self.http_client.get(url_completa)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            clubes = []
            tabla = soup.find('table', class_='items')
            
            if tabla:
                filas = tabla.find_all('tr')
                
                for fila in filas:
                    try:
                        celdas = fila.find_all('td')
                        if len(celdas) < 4:
                            continue
                        
                        links_clubes = fila.find_all('a', href=lambda x: x and '/verein/' in x and '/spieler/' not in x)
                        
                        for link_club in links_clubes:
                            nombre_club = link_club.text.strip()
                            
                            if not self._es_club_valido(nombre_club):
                                continue
                            
                            if self._es_duplicado(nombre_club, clubes):
                                continue
                            
                            pais = 'Desconocido'
                            parent = link_club.parent
                            if parent:
                                img_bandera = parent.find('img', class_='flaggenrahmen')
                                if img_bandera:
                                    pais = img_bandera.get('title', 'Desconocido')
                                    if not pais or pais == '':
                                        pais = img_bandera.get('alt', 'Desconocido')
                            
                            periodo = None
                            if len(celdas) > 0:
                                fecha_text = celdas[1].text.strip() if len(celdas) > 1 else celdas[0].text.strip()
                                if fecha_text and len(fecha_text) < 50:
                                    periodo = fecha_text
                            
                            clubes.append({
                                'nombre': nombre_club,
                                'pais': pais,
                                'periodo': periodo
                            })
                    
                    except Exception:
                        continue
            
            return clubes
        
        except Exception:
            return []
    
    def _extraer_desde_perfil(self, url_perfil: str) -> List[Dict]:
        """
        Método alternativo: extraer clubes desde la página de perfil
        
        Args:
            url_perfil: URL del perfil
        
        Returns:
            Lista de clubes
        """
        try:
            url_completa = f"{self.settings.TRANSFERMARKT_BASE_URL}{url_perfil}"
            response = self.http_client.get(url_completa)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            clubes = []
            
            # MÉTODO 1: Buscar en la sección de "Trayectoria como jugador"
            boxes = soup.find_all('div', class_='box')
            
            for box in boxes:
                titulo = box.find('h2')
                if not titulo:
                    continue
                
                texto_titulo = titulo.text.strip().lower()
                
                if any(palabra in texto_titulo for palabra in ['trayectoria', 'historia', 'stations', 'career']):
                    tabla = box.find('table', class_='items')
                    
                    if tabla:
                        filas = tabla.find_all('tr')
                        
                        for fila in filas:
                            try:
                                celdas = fila.find_all('td')
                                if len(celdas) < 2:
                                    continue
                                
                                link_club = fila.find('a', href=lambda x: x and '/verein/' in x)
                                if not link_club:
                                    continue
                                
                                nombre_club = link_club.text.strip()
                                
                                if not self._es_club_valido(nombre_club):
                                    continue
                                
                                if self._es_duplicado(nombre_club, clubes):
                                    continue
                                
                                pais = 'Desconocido'
                                img_bandera = fila.find('img', class_='flaggenrahmen')
                                if img_bandera:
                                    pais = img_bandera.get('title', 'Desconocido')
                                    if not pais or pais == '':
                                        pais = img_bandera.get('alt', 'Desconocido')
                                
                                periodo = None
                                for celda in celdas:
                                    texto = celda.text.strip()
                                    if '-' in texto or any(mes in texto.lower() for mes in ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sep', 'oct', 'nov', 'dic']):
                                        periodo = texto
                                        break
                                
                                clubes.append({
                                    'nombre': nombre_club,
                                    'pais': pais,
                                    'periodo': periodo
                                })
                            
                            except Exception:
                                continue
            
            # MÉTODO 2: Si no encontramos clubes, buscar en tablas de rendimiento
            if not clubes:
                clubes = self._extraer_clubes_desde_rendimiento(soup)
            
            # MÉTODO 3: Buscar en cualquier tabla con links de clubes
            if not clubes:
                clubes = self._extraer_clubes_general(soup)
            
            return clubes
        
        except Exception:
            return []
    
    def _extraer_clubes_desde_rendimiento(self, soup) -> List[Dict]:
        """
        Método alternativo para extraer clubes desde la tabla de rendimiento
        
        Args:
            soup: BeautifulSoup del perfil
        
        Returns:
            Lista de clubes
        """
        clubes = []
        
        try:
            # Buscar tabla de rendimiento por club
            tablas_stats = soup.find_all('table', class_='items')
            
            for tabla in tablas_stats:
                # Verificar si es la tabla de estadísticas por club
                encabezado = tabla.find_previous('h2')
                if not encabezado or 'club' not in encabezado.text.lower():
                    continue
                
                filas = tabla.find_all('tr', class_=['odd', 'even'])
                
                for fila in filas:
                    try:
                        celdas = fila.find_all('td')
                        if len(celdas) < 2:
                            continue
                        
                        # Primera celda suele tener el nombre del club
                        celda_club = celdas[0]
                        link_club = celda_club.find('a')
                        
                        if link_club:
                            nombre_club = link_club.get('title', '').strip()
                            if not nombre_club:
                                nombre_club = link_club.text.strip()
                            
                            # Validar nombre del club
                            if not self._es_club_valido(nombre_club):
                                continue
                            
                            # Buscar bandera para el país
                            pais = 'Desconocido'
                            img_bandera = celda_club.find('img', class_='flaggenrahmen')
                            if img_bandera:
                                pais = img_bandera.get('title', 'Desconocido')
                            
                            # Evitar duplicados
                            if not self._es_duplicado(nombre_club, clubes):
                                clubes.append({
                                    'nombre': nombre_club,
                                    'pais': pais,
                                    'periodo': None
                                })
                    
                    except Exception:
                        continue
        
        except Exception:
            pass
        
        return clubes
    
    def _es_club_valido(self, nombre: str) -> bool:
        """
        Verifica si un nombre es un club válido
        
        Args:
            nombre: Nombre del club a verificar
        
        Returns:
            True si es válido, False si no
        """
        # Convertir a minúsculas para comparación
        nombre_lower = nombre.lower()
        
        # Lista de palabras clave que indican que NO es un club
        palabras_invalidas = [
            'nuevo fichaje', 'fichaje', 'transferencia',
            'selección', 'selection', 'nacional', 'national',
            's20', 's21', 's23', 'u20', 'u21', 'u23',
            'sin club', 'free agent', 'retirado', 'retired',
            'a prueba', 'trial', 'préstamo', 'loan'
        ]
        
        # Verificar si contiene alguna palabra inválida
        if any(palabra in nombre_lower for palabra in palabras_invalidas):
            return False
        
        # Verificar que no sea solo un país (muy corto)
        if len(nombre) < 5:
            return False
        
        # Verificar que no sea solo números
        if nombre.replace(' ', '').isdigit():
            return False
        
        return True
    
    def _normalizar_nombre_club(self, nombre: str) -> str:
        """
        Normaliza el nombre de un club para detectar duplicados
        
        Args:
            nombre: Nombre original del club
        
        Returns:
            Nombre normalizado
        """
        # Remover prefijos comunes
        nombre_norm = nombre
        prefijos = ['CA ', 'Club ', 'CF ', 'CD ', 'FC ', 'AC ', 'RC ', 'SC ']
        for prefijo in prefijos:
            if nombre_norm.startswith(prefijo):
                nombre_norm = nombre_norm[len(prefijo):]
        
        # Convertir a minúsculas y remover espacios extras
        nombre_norm = ' '.join(nombre_norm.lower().split())
        
        return nombre_norm
    
    def _es_duplicado(self, nombre: str, clubes: List[Dict]) -> bool:
        """
        Verifica si un club ya está en la lista (incluyendo variantes)
        
        Args:
            nombre: Nombre del club a verificar
            clubes: Lista de clubes existentes
        
        Returns:
            True si es duplicado, False si no
        """
        nombre_norm = self._normalizar_nombre_club(nombre)
        
        for club in clubes:
            club_norm = self._normalizar_nombre_club(club['nombre'])
            
            # Si son iguales después de normalizar, es duplicado
            if nombre_norm == club_norm:
                return True
            
            # Si uno contiene al otro (ej: "Rosario Central" y "CA Rosario Central")
            if nombre_norm in club_norm or club_norm in nombre_norm:
                return True
        
        return False
    
    def _extraer_clubes_general(self, soup) -> List[Dict]:
        """
        Método general para extraer clubes de cualquier tabla
        
        Args:
            soup: BeautifulSoup del perfil
        
        Returns:
            Lista de clubes
        """
        clubes = []
        
        try:
            # Buscar TODOS los links que apunten a clubes
            links_clubes = soup.find_all('a', href=lambda x: x and '/verein/' in x and '/spieler/' not in x)
            
            for link in links_clubes:
                try:
                    nombre_club = link.text.strip()
                    
                    # Filtrar nombres inválidos
                    if not self._es_club_valido(nombre_club):
                        continue
                    
                    # Evitar duplicados inteligentemente
                    if self._es_duplicado(nombre_club, clubes):
                        continue
                    
                    # Buscar país cerca del link
                    pais = 'Desconocido'
                    
                    # Buscar en el padre
                    parent = link.parent
                    if parent:
                        img_bandera = parent.find('img', class_='flaggenrahmen')
                        if img_bandera:
                            pais = img_bandera.get('title', 'Desconocido')
                            if not pais or pais == '':
                                pais = img_bandera.get('alt', 'Desconocido')
                    
                    # Buscar en el abuelo si no encontró en el padre
                    if pais == 'Desconocido' and parent and parent.parent:
                        img_bandera = parent.parent.find('img', class_='flaggenrahmen')
                        if img_bandera:
                            pais = img_bandera.get('title', 'Desconocido')
                    
                    clubes.append({
                        'nombre': nombre_club,
                        'pais': pais,
                        'periodo': None
                    })
                    
                    # Limitar a un máximo razonable
                    if len(clubes) >= 15:
                        break
                
                except Exception:
                    continue
        
        except Exception:
            pass
        
        return clubes
    
    def jugador_tiene_historia_completa(self, jugador_data: Dict) -> bool:
        """
        Verifica si un jugador ya tiene la historia de clubes completa
        
        Args:
            jugador_data: Diccionario con datos del jugador
        
        Returns:
            True si ya tiene historia completa, False si no
        """
        return (
            'clubes_historia' in jugador_data and
            jugador_data['clubes_historia'] is not None and
            isinstance(jugador_data['clubes_historia'], list) and
            len(jugador_data['clubes_historia']) > 0
        )
