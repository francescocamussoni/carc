"""
Servicio para extraer goles detallados de jugadores desde Transfermarkt
"""

from typing import List, Optional
from bs4 import BeautifulSoup
import re
from ..config import Settings
from ..utils import HTTPClient
from ..models import GolIndividual


class GolesDetalladosService:
    """
    Servicio para obtener goles con información detallada (rival, minuto, tipo, etc.)
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
    
    def obtener_goles_jugador(self, url_perfil: str, nombre_jugador: str) -> List[GolIndividual]:
        """
        Obtiene todos los goles del jugador con información detallada
        
        Args:
            url_perfil: URL del perfil del jugador (ej: /marco-ruben/profil/spieler/30825)
            nombre_jugador: Nombre del jugador (para logging)
        
        Returns:
            Lista de GolIndividual con información completa de cada gol
        """
        try:
            # Construir URL de la página de goles SIN FILTRO (luego filtramos en código)
            url_goles = url_perfil.replace('/profil/', '/alletore/')
            url_completa = f"{self.settings.TRANSFERMARKT_BASE_URL}{url_goles}"
            
            print(f"      🔍 Obteniendo goles de {nombre_jugador}...")
            
            response = self.http_client.get(url_completa, use_cache=True)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Buscar todas las tablas (la segunda suele ser la de goles)
            tablas = soup.find_all('table')
            tabla_goles = None
            
            for tabla in tablas:
                tbody = tabla.find('tbody')
                if tbody and len(tbody.find_all('tr')) > 10:  # Tabla grande
                    tabla_goles = tabla
                    break
            
            if not tabla_goles:
                print(f"      ℹ️  No hay tabla de goles para {nombre_jugador}")
                return []
            
            # Extraer goles con toda la información
            goles_list = self._extraer_goles_de_tabla(tabla_goles)
            
            print(f"      ✅ {len(goles_list)} goles extraídos con información detallada")
            return goles_list
        
        except Exception as e:
            print(f"      ⚠️  Error obteniendo goles de {nombre_jugador}: {e}")
            return []
    
    def _extraer_goles_de_tabla(self, tabla) -> List[GolIndividual]:
        """
        Extrae goles de la tabla con información completa
        
        IMPORTANTE: 
        - Filas con >=10 celdas = nuevo partido
        - Filas con 3-9 celdas = gol adicional en el mismo partido
        
        Returns:
            Lista de GolIndividual
        """
        goles_list = []
        temporada_actual = ""
        
        # Variables para el partido actual (para filas de continuación)
        partido_actual = {
            'club': '',
            'competicion': '',
            'rival': '',
            'marcador_final': '',
            'local_visitante': ''
        }
        
        tbody = tabla.find('tbody')
        if not tbody:
            return []
        
        filas = tbody.find_all('tr')
        
        for fila in filas:
            celdas = fila.find_all(['td', 'th'])
            num_celdas = len(celdas)
            
            # Fila de separador (1 celda) = nueva temporada
            if num_celdas == 1:
                texto = celdas[0].text.strip()
                if 'Temporada' in texto or 'temporada' in texto:
                    temporada_actual = texto
                continue
            
            # Fila completa (>=10 celdas) = NUEVO PARTIDO
            if num_celdas >= 10:
                try:
                    # Verificar club (celda 3 - logo del club del jugador)
                    club_cell = celdas[3] if len(celdas) > 3 else None
                    club_nombre = ""
                    if club_cell:
                        img = club_cell.find('img')
                        if img:
                            club_nombre = img.get('alt', img.get('title', ''))
                    
                    # Filtrar solo Rosario Central
                    if 'Rosario Central' not in club_nombre:
                        partido_actual = {}
                        continue
                    
                    # Extraer información del partido
                    # Celda 0: Competición (icono)
                    competicion = self._extraer_competicion(celdas[0])
                    
                    # Celda 2: Local/Visitante
                    local_visitante = celdas[2].text.strip() if len(celdas) > 2 else ""
                    
                    # Celda 5 o 6: Rival
                    rival = self._extraer_rival(celdas)
                    
                    # Celda 7: Marcador final
                    marcador_final = celdas[7].text.strip() if len(celdas) > 7 else ""
                    
                    # Celda 9: Minuto
                    minuto = celdas[9].text.strip() if len(celdas) > 9 else ""
                    
                    # Celda 10: Marcador momento
                    marcador_momento = celdas[10].text.strip() if len(celdas) > 10 else ""
                    
                    # Celda 11: Tipo de gol
                    tipo_gol = celdas[11].text.strip() if len(celdas) > 11 else ""
                    
                    # Guardar partido actual para filas de continuación
                    partido_actual = {
                        'club': club_nombre,
                        'competicion': competicion,
                        'rival': rival,
                        'marcador_final': marcador_final,
                        'local_visitante': local_visitante
                    }
                    
                    # Crear gol
                    if rival:
                        gol = GolIndividual(
                            rival=rival,
                            competicion=competicion,
                            temporada=temporada_actual,
                            minuto=minuto,
                            tipo_gol=tipo_gol,
                            marcador_momento=marcador_momento,
                            marcador_final=marcador_final,
                            local_visitante=local_visitante
                        )
                        goles_list.append(gol)
                
                except Exception as e:
                    partido_actual = {}
                    continue
            
            # Fila de continuación (3-9 celdas) = GOL ADICIONAL en mismo partido
            elif 3 <= num_celdas < 10 and partido_actual.get('rival'):
                try:
                    # Celda 1: Minuto (o puede estar en otra posición)
                    minuto = ""
                    marcador_momento = ""
                    tipo_gol = ""
                    
                    # Buscar minuto (formato "XX'" o "XX'+X")
                    for celda in celdas[:3]:
                        texto = celda.text.strip()
                        if "'" in texto or '+' in texto:
                            minuto = texto
                            break
                    
                    # Buscar marcador (formato "X:X")
                    for celda in celdas:
                        texto = celda.text.strip()
                        if ':' in texto and re.match(r'\d+:\d+', texto):
                            marcador_momento = texto
                            break
                    
                    # Buscar tipo de gol (última celda con texto largo)
                    for celda in reversed(celdas):
                        texto = celda.text.strip()
                        if len(texto) > 5 and ':' not in texto:
                            tipo_gol = texto
                            break
                    
                    # Crear gol adicional con info del partido actual
                    gol = GolIndividual(
                        rival=partido_actual['rival'],
                        competicion=partido_actual['competicion'],
                        temporada=temporada_actual,
                        minuto=minuto,
                        tipo_gol=tipo_gol,
                        marcador_momento=marcador_momento,
                        marcador_final=partido_actual['marcador_final'],
                        local_visitante=partido_actual['local_visitante']
                    )
                    goles_list.append(gol)
                
                except Exception:
                    continue
        
        return goles_list
    
    def _extraer_competicion(self, celda) -> str:
        """Extrae el nombre de la competición de la celda con icono"""
        img = celda.find('img')
        if img:
            comp = img.get('title', '').strip()
            if comp:
                return comp
        return ""
    
    def _extraer_rival(self, celdas: list) -> str:
        """Extrae el nombre del rival de las celdas 5 o 6"""
        # Intentar celda 5 (suele tener logo + nombre)
        if len(celdas) > 5:
            texto = celdas[5].text.strip()
            if texto and len(texto) > 2:
                return self._limpiar_nombre_rival(texto)
        
        # Intentar celda 6
        if len(celdas) > 6:
            texto = celdas[6].text.strip()
            if texto and len(texto) > 3 and not texto.isdigit():
                return self._limpiar_nombre_rival(texto)
        
        return ""
    
    def _limpiar_nombre_rival(self, texto: str) -> str:
        """Limpia el nombre del rival removiendo posiciones entre paréntesis"""
        # Remover "(posición)" al final, ej: "Boca Juniors  (3.)" -> "Boca Juniors"
        texto = re.sub(r'\s*\(\d+\.\)$', '', texto)
        return texto.strip()
