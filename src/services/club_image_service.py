"""
Servicio para descargar imágenes de clubes desde Transfermarkt.
"""

import re
from pathlib import Path
from typing import Optional, Set, Dict
from bs4 import BeautifulSoup

from ..config import Settings
from ..utils import HTTPClient, TextUtils


class ClubImageService:
    """
    Servicio para descarga de escudos de clubes desde Transfermarkt.
    """
    
    def __init__(self, settings: Optional[Settings] = None, http_client: Optional[HTTPClient] = None):
        """
        Inicializa el servicio de imágenes de clubes.
        
        Args:
            settings: Instancia de Settings (opcional)
            http_client: Cliente HTTP (opcional)
        """
        self.settings = settings or Settings()
        self.http_client = http_client or HTTPClient(self.settings)
        self.base_url = "https://www.transfermarkt.es"
        
        # IDs conocidos de clubes grandes que a veces no aparecen en búsqueda rápida
        # Formato: 'nombre': id_transfermarkt
        self.clubes_conocidos = {
            # Europa
            'as roma': 12,
            'roma': 12,
            'ss lazio': 398,
            'lazio': 398,
            'inter': 46,
            'fc barcelona': 131,
            'barcelona': 131,
            'real madrid': 418,
            'bayern munich': 27,
            'bayern': 27,
            'manchester united': 985,
            'man. united': 985,
            'manchester city': 281,
            'man. city': 281,
            'chelsea': 631,
            'arsenal': 11,
            'liverpool': 31,
            
            # Sudamérica
            'river plate': 209,
            'boca juniors': 189,
            'racing club': 1444,
            'racing': 1444,
            'independiente': 1040,
            'san lorenzo': 1029,
            'estudiantes': 1083,
            'gimnasia': 1106,
            'rosario central': 1418,
            'rio ave': 1496,
            'rio ave fc': 1496,
            'sporting cristal': 6362,
            'sport. cristal': 6362,
            'universidad católica': 2076,
            'u. católica': 2076,
            'universidad de chile': 2077,
            'u. de chile': 2077,
        }
    
    def buscar_y_descargar_escudo(self, nombre_club: str, pais: str = "") -> Optional[str]:
        """
        Busca un club en Transfermarkt y descarga su escudo.
        
        Args:
            nombre_club: Nombre del club
            pais: País del club (opcional, ayuda a disambiguar)
        
        Returns:
            Ruta relativa del escudo descargado o None si falla
        """
        try:
            # Buscar club en Transfermarkt
            club_url = self._buscar_club(nombre_club, pais)
            if not club_url:
                print(f"      ⚠️  No se encontró {nombre_club}")
                return None
            
            # Extraer URL del escudo
            escudo_url = self._extraer_url_escudo(club_url)
            if not escudo_url:
                print(f"      ⚠️  No se pudo extraer escudo de {nombre_club}")
                return None
            
            # Descargar escudo
            return self._descargar_escudo(escudo_url, nombre_club)
        
        except Exception as e:
            print(f"      ⚠️  Error con {nombre_club}: {e}")
            return None
    
    def _buscar_club(self, nombre_club: str, pais: str = "") -> Optional[str]:
        """
        Busca un club en Transfermarkt y retorna su URL.
        
        Args:
            nombre_club: Nombre del club
            pais: País del club
        
        Returns:
            URL del club o None si no se encuentra
        """
        # Verificar primero en clubes conocidos
        nombre_lower = nombre_club.lower().strip()
        if nombre_lower in self.clubes_conocidos:
            club_id = self.clubes_conocidos[nombre_lower]
            # Construir URL directa
            club_slug = nombre_lower.replace(' ', '-')
            return f"{self.base_url}/{club_slug}/startseite/verein/{club_id}"
        
        # Generar variaciones del nombre para buscar
        variaciones = [
            nombre_club.strip(),
        ]
        
        # Agregar variación sin abreviaciones
        nombre_expandido = nombre_club.lower()
        expansiones = {
            'u.': 'universidad',
            'dep.': 'deportivo', 
            'sport.': 'sporting',
            'man.': 'manchester',
            'gim.': 'gimnasia',
            'est.': 'estudiantes',
        }
        for abrev, completo in expansiones.items():
            if abrev in nombre_expandido:
                variaciones.append(nombre_expandido.replace(abrev, completo))
        
        # Si tiene prefijos como "AS", "FC", "CD", agregar versión sin ellos
        palabras = nombre_club.split()
        if len(palabras) > 1:
            prefijos = ['as', 'fc', 'cd', 'ca', 'cf', 'ac', 'sc', 'ss']
            if palabras[0].lower() in prefijos:
                # Agregar versión sin el prefijo
                variaciones.append(' '.join(palabras[1:]))
        
        # Agregar versión normalizada
        variaciones.append(self._normalizar_nombre_club(nombre_club))
        
        # Eliminar duplicados manteniendo orden
        variaciones_unicas = []
        for v in variaciones:
            v_clean = v.strip()
            if v_clean and v_clean not in variaciones_unicas:
                variaciones_unicas.append(v_clean)
        
        # Intentar con cada variación
        for nombre_busqueda in variaciones_unicas:
            url = self._buscar_club_variacion(nombre_busqueda, pais, nombre_club)
            if url:
                return url
        
        return None
    
    def _buscar_club_variacion(self, nombre_busqueda: str, pais: str, nombre_original: str) -> Optional[str]:
        """
        Busca un club con una variación específica del nombre.
        
        Args:
            nombre_busqueda: Variación del nombre a buscar
            pais: País del club
            nombre_original: Nombre original del club (para comparación)
        
        Returns:
            URL del club o None
        """
        # URL de búsqueda
        search_url = f"{self.base_url}/schnellsuche/ergebnis/schnellsuche?query={nombre_busqueda}&Verein_page=0"
        
        try:
            response = self.http_client.get(search_url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Buscar tabla de resultados de clubes
            tabla_clubes = soup.find('table', class_='items')
            if not tabla_clubes:
                return None
            
            # Recoger TODOS los clubes candidatos
            candidatos = []
            rows = tabla_clubes.find_all('tr', class_=['odd', 'even'])
            
            for row in rows:
                # Buscar links de clubes (verein/startseite)
                club_links = row.find_all('a', href=lambda x: x and 'verein' in x and 'startseite' in x)
                
                for club_link in club_links:
                    nombre_encontrado = club_link.get_text(strip=True)
                    
                    # Si el nombre coincide razonablemente
                    if self._nombres_similares(nombre_original, nombre_encontrado):
                        # Obtener país
                        pais_cell = row.find('img', {'class': 'flaggenrahmen'})
                        pais_encontrado = pais_cell.get('title', '') if pais_cell else ''
                        
                        # Calcular score de coincidencia
                        score = 0
                        if pais and pais != "Desconocido" and pais_encontrado == pais:
                            score += 100  # País coincide exactamente
                        
                        # Normalizar nombres y comparar
                        norm_original = self._normalizar_nombre_club(nombre_original)
                        norm_encontrado = self._normalizar_nombre_club(nombre_encontrado)
                        
                        if norm_original == norm_encontrado:
                            score += 50  # Coincidencia exacta normalizada
                        elif norm_original in norm_encontrado or norm_encontrado in norm_original:
                            score += 30  # Coincidencia parcial
                        
                        href = club_link['href']
                        if '/startseite/' not in href:
                            href = href.replace('/kader/', '/startseite/')
                        
                        candidatos.append((score, self.base_url + href, nombre_encontrado, pais_encontrado))
            
            # Si hay candidatos, retornar el de mayor score
            if candidatos:
                candidatos.sort(key=lambda x: x[0], reverse=True)
                # Si el mejor candidato tiene score > 0, retornarlo
                if candidatos[0][0] > 0:
                    return candidatos[0][1]
                # Si todos tienen score 0 pero hay coincidencia de país, tomar ese
                for score, url, nombre, pais_enc in candidatos:
                    if pais and pais != "Desconocido" and pais_enc == pais:
                        return url
                # Si no, tomar el primero
                return candidatos[0][1]
            
            return None
        
        except Exception as e:
            return None
    
    def _extraer_url_escudo(self, club_url: str) -> Optional[str]:
        """
        Extrae la URL del escudo desde la página del club.
        
        Args:
            club_url: URL de la página del club
        
        Returns:
            URL del escudo o None
        """
        try:
            response = self.http_client.get(club_url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Buscar imagen del escudo en tamaño grande (wappen/head/)
            # Esta es la imagen principal del club, no el logo de Transfermarkt
            all_imgs = soup.find_all('img', src=True)
            
            for img in all_imgs:
                src = img.get('src', '')
                # Buscar escudo en formato wappen/head/ (tamaño grande)
                if 'wappen/head/' in src or 'wappen/headerRund/' in src:
                    return src
            
            # Si no encuentra en head, buscar en cualquier wappen que no sea tiny
            for img in all_imgs:
                src = img.get('src', '')
                if 'wappen' in src and 'tiny' not in src and src.startswith('http'):
                    # Extraer el ID del club y construir URL del escudo grande
                    match = re.search(r'/wappen/[^/]+/(\d+)\.', src)
                    if match:
                        club_id = match.group(1)
                        # Construir URL del escudo en tamaño head
                        return f"https://tmssl.akamaized.net/images/wappen/head/{club_id}.png"
            
            return None
        
        except Exception as e:
            print(f"      ⚠️  Error extrayendo escudo: {e}")
            return None
    
    def _descargar_escudo(self, escudo_url: str, nombre_club: str) -> Optional[str]:
        """
        Descarga el escudo del club.
        
        Args:
            escudo_url: URL del escudo
            nombre_club: Nombre del club
        
        Returns:
            Ruta relativa del escudo guardado o None
        """
        try:
            # Limpiar nombre para archivo
            nombre_archivo = TextUtils.limpiar_nombre_archivo(nombre_club)
            
            # Obtener extensión
            extension = self._extraer_extension(escudo_url)
            
            # Rutas
            ruta_completa = self.settings.CLUBES_IMAGES_DIR / f"{nombre_archivo}{extension}"
            ruta_relativa = f"data/images/clubes/{nombre_archivo}{extension}"
            
            # Si ya existe, no descargar
            if ruta_completa.exists():
                return ruta_relativa
            
            # Descargar
            response = self.http_client.get(escudo_url)
            
            # Guardar
            with open(ruta_completa, 'wb') as f:
                f.write(response.content)
            
            return ruta_relativa
        
        except Exception as e:
            print(f"      ⚠️  Error descargando escudo: {e}")
            return None
    
    def _extraer_extension(self, url: str) -> str:
        """Extrae extensión de la URL."""
        extension = '.png'  # Default para escudos
        if '.' in url:
            ext_match = re.search(r'\.(jpg|jpeg|png|gif|webp|svg)', url.lower())
            if ext_match:
                extension = '.' + ext_match.group(1)
        return extension
    
    def _normalizar_nombre_club(self, nombre: str) -> str:
        """
        Normaliza el nombre de un club para comparación.
        
        Args:
            nombre: Nombre del club
        
        Returns:
            Nombre normalizado
        """
        # Convertir a minúsculas
        nombre = nombre.lower().strip()
        
        # Expandir abreviaciones comunes
        abreviaciones = {
            'u.': 'universidad',
            'dep.': 'deportivo',
            'sport.': 'sporting',
            'man.': 'manchester',
            'cs': 'club sportivo',
            'gim.': 'gimnasia',
            'est.': 'estudiantes',
            'ind.': 'independiente',
            'atl.': 'atletico',
        }
        
        for abrev, completo in abreviaciones.items():
            if nombre.startswith(abrev + ' '):
                nombre = nombre.replace(abrev + ' ', completo + ' ', 1)
        
        # Remover palabras comunes y artículos
        palabras_comunes = [
            'club', 'atletico', 'deportivo', 'fc', 'cf', 'ca', 'de', 'del', 
            'la', 'el', 'los', 'las', 'cd', 'ac', 'sc', 'as', 'ss',
            'asociacion', 'sociedad', 'sport', 'sports'
        ]
        
        palabras = nombre.split()
        palabras_filtradas = [p for p in palabras if p not in palabras_comunes]
        
        # Si quedó vacío, usar original sin filtrar tanto
        if not palabras_filtradas:
            palabras_filtradas = [p for p in palabras if p not in ['de', 'del', 'la', 'el']]
        
        return ' '.join(palabras_filtradas).strip()
    
    def _nombres_similares(self, nombre1: str, nombre2: str) -> bool:
        """
        Verifica si dos nombres de clubes son similares.
        
        Args:
            nombre1: Primer nombre
            nombre2: Segundo nombre
        
        Returns:
            True si son similares, False si no
        """
        # Normalizar ambos nombres
        n1 = self._normalizar_nombre_club(nombre1)
        n2 = self._normalizar_nombre_club(nombre2)
        
        # Si alguno está vacío, no son similares
        if not n1 or not n2:
            return False
        
        # Comparación exacta
        if n1 == n2:
            return True
        
        # Uno contiene al otro
        if n1 in n2 or n2 in n1:
            return True
        
        # Comparar palabras individuales (al menos una palabra clave en común)
        palabras1 = set(n1.split())
        palabras2 = set(n2.split())
        
        # Si hay intersección significativa (al menos 50% de palabras en común)
        if palabras1 and palabras2:
            interseccion = palabras1.intersection(palabras2)
            min_palabras = min(len(palabras1), len(palabras2))
            if len(interseccion) >= max(1, min_palabras * 0.5):
                return True
        
        return False
