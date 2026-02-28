"""
Servicio para extraer información básica de técnicos desde Transfermarkt
"""

from typing import List, Optional, Tuple
from bs4 import BeautifulSoup
import re

from ..config import Settings
from ..utils import HTTPClient
from ..models import Tecnico, ClubTecnico, EstadisticaTorneo


class TecnicoService:
    """
    Servicio para obtener información básica de técnicos
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
    
    def obtener_tecnicos_rosario_central(self) -> List[Tuple[str, str, str, int]]:
        """
        Obtiene la lista de técnicos que dirigieron Rosario Central
        
        Returns:
            Lista de tuplas (nombre, url_perfil, periodo, partidos)
        """
        try:
            print(f"🔍 Obteniendo lista de técnicos de Rosario Central...")
            
            response = self.http_client.get(self.settings.TRANSFERMARKT_MITARBEITER_URL)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Buscar tabla de técnicos
            tabla = soup.find('table', class_='items')
            
            if not tabla:
                print("⚠️  No se encontró la tabla de técnicos")
                return []
            
            tecnicos = []
            tbody = tabla.find('tbody')
            
            if tbody:
                filas = tbody.find_all('tr', class_=['odd', 'even'])
                
                for fila in filas:
                    try:
                        # Extraer información del técnico (ahora incluye partidos)
                        nombre, url, periodo, partidos = self._extraer_info_tecnico(fila)
                        
                        if nombre and url:
                            tecnicos.append((nombre, url, periodo, partidos))
                    
                    except Exception as e:
                        print(f"      ⚠️  Error procesando fila: {e}")
                        continue
            
            print(f"✅ {len(tecnicos)} técnicos encontrados")
            return tecnicos
        
        except Exception as e:
            print(f"❌ Error obteniendo técnicos: {e}")
            return []
    
    def _extraer_info_tecnico(self, fila) -> Tuple[str, str, str, int]:
        """
        Extrae información básica de un técnico desde una fila de la tabla
        
        Returns:
            Tupla (nombre, url_perfil, periodo, partidos)
        """
        celdas = fila.find_all(['td', 'th'])
        
        if len(celdas) < 3:
            return ("", "", "", 0)
        
        # Celda 2: Nombre y URL
        nombre = ""
        url = ""
        nombre_cell = celdas[2]
        link = nombre_cell.find('a', href=re.compile(r'/profil/trainer/'))
        if link:
            nombre = link.text.strip()
            url = link.get('href', '')
        
        # Celdas 5-6: Periodo (fecha inicio - fecha fin)
        periodo = ""
        fecha_inicio = ""
        fecha_fin = ""
        
        if len(celdas) > 5:
            fecha_inicio = celdas[5].text.strip()
        if len(celdas) > 6:
            fecha_fin = celdas[6].text.strip()
        
        if fecha_inicio:
            periodo = fecha_inicio
            if fecha_fin:
                periodo += f" - {fecha_fin}"
            elif "actualidad" not in periodo.lower():
                periodo += " - Actualidad"
        
        # Celda 8: Partidos dirigidos
        partidos = 0
        if len(celdas) > 8:
            try:
                partidos = int(celdas[8].text.strip())
            except:
                partidos = 0
        
        return (nombre, url, periodo, partidos)
    
    def obtener_info_completa_tecnico(self, url_perfil: str, nombre: str) -> Optional[Tecnico]:
        """
        Obtiene información completa de un técnico desde su perfil
        
        Args:
            url_perfil: URL del perfil del técnico
            nombre: Nombre del técnico (para logging)
        
        Returns:
            Objeto Tecnico con información completa o None
        """
        try:
            print(f"   📋 {nombre}")
            
            url_completa = f"{self.settings.TRANSFERMARKT_BASE_URL}{url_perfil}"
            response = self.http_client.get(url_completa, use_cache=True)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extraer información básica
            nacionalidad = self._extraer_nacionalidad(soup)
            fecha_nac = self._extraer_fecha_nacimiento(soup)
            edad = self._extraer_edad(soup)
            
            tecnico = Tecnico(
                nombre=nombre,
                url_perfil=url_perfil,
                nacionalidad=nacionalidad,
                fecha_nacimiento=fecha_nac,
                edad=edad
            )
            
            return tecnico
        
        except Exception as e:
            print(f"      ⚠️  Error obteniendo info de {nombre}: {e}")
            return None
    
    def _extraer_nacionalidad(self, soup) -> str:
        """Extrae la nacionalidad del técnico"""
        try:
            # Buscar en el perfil principal
            info_table = soup.find('div', class_='info-table')
            if info_table:
                spans = info_table.find_all('span', class_='info-table__content')
                for span in spans:
                    img = span.find('img', class_='flaggenrahmen')
                    if img:
                        return img.get('title', '').strip()
        except:
            pass
        return ""
    
    def _extraer_fecha_nacimiento(self, soup) -> str:
        """Extrae la fecha de nacimiento"""
        try:
            info_table = soup.find('div', class_='info-table')
            if info_table:
                spans = info_table.find_all('span', class_='info-table__content')
                for span in spans:
                    texto = span.text.strip()
                    # Buscar formato de fecha
                    if '/' in texto or '.' in texto:
                        # Puede ser una fecha
                        match = re.search(r'\d{1,2}[/.-]\d{1,2}[/.-]\d{4}', texto)
                        if match:
                            return match.group()
        except:
            pass
        return ""
    
    def _extraer_edad(self, soup) -> str:
        """Extrae la edad"""
        try:
            info_table = soup.find('div', class_='info-table')
            if info_table:
                spans = info_table.find_all('span', class_='info-table__content')
                for span in spans:
                    texto = span.text.strip()
                    # Buscar formato "XX años"
                    match = re.search(r'(\d+)\s*años?', texto, re.IGNORECASE)
                    if match:
                        return match.group(1)
        except:
            pass
        return ""
