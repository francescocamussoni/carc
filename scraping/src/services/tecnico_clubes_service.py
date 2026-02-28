"""
Servicio para extraer la historia de clubes de un técnico
"""

from typing import List, Optional
from bs4 import BeautifulSoup
import re

from ..config import Settings
from ..utils import HTTPClient
from ..models import ClubTecnico


class TecnicoClubesService:
    """
    Servicio para obtener todos los clubes que dirigió un técnico
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
    
    def obtener_clubes_tecnico(self, url_perfil: str, nombre_tecnico: str) -> List[ClubTecnico]:
        """
        Obtiene todos los clubes que dirigió el técnico
        
        Args:
            url_perfil: URL del perfil del técnico
            nombre_tecnico: Nombre del técnico (para logging)
        
        Returns:
            Lista de ClubTecnico con información de cada club
        """
        try:
            # Construir URL de la página de estaciones
            # De /profil/trainer/XXX a /stationen/trainer/XXX
            url_estaciones = url_perfil.replace('/profil/', '/stationen/')
            url_completa = f"{self.settings.TRANSFERMARKT_BASE_URL}{url_estaciones}"
            
            # print(f"      🏆 Obteniendo clubes dirigidos...")
            
            response = self.http_client.get(url_completa, use_cache=True)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # USAR SIEMPRE el método de tabla estándar con filtro de "Entrenador"
            # Este método ya incluye el filtro para excluir asistentes, interinos, etc.
            clubes = self._extraer_de_tabla_estandar(soup)
            
            # Solo mostrar si encontramos clubes
            if clubes:
                print(f"      ✅ {len(clubes)} clubes encontrados")
            
            return clubes
        
        except Exception as e:
            # Silenciar error, es esperado para algunos técnicos
            return []
    
    def _extraer_club_de_fila(self, fila) -> Optional[ClubTecnico]:
        """Extrae información de un club desde una fila"""
        try:
            # Buscar nombre del club
            club_link = fila.find('a', href=re.compile(r'/verein/\d+'))
            if not club_link:
                return None
            
            club_nombre = club_link.text.strip()
            
            # Buscar país (imagen de bandera)
            pais = ""
            img = fila.find('img', class_='flaggenrahmen')
            if img:
                pais = img.get('title', '').strip()
            
            # Buscar periodo
            periodo = ""
            periodo_spans = fila.find_all('span', string=re.compile(r'\d{2}\.\d{2}\.\d{4}'))
            if periodo_spans:
                periodos_texto = [s.text.strip() for s in periodo_spans]
                if periodos_texto:
                    periodo = ' - '.join(periodos_texto[:2])  # Inicio - Fin
            
            if club_nombre:
                return ClubTecnico(
                    club=self._normalizar_nombre_club(club_nombre),
                    pais=pais,
                    periodo=periodo
                )
        
        except Exception:
            pass
        
        return None
    
    def _extraer_de_tabla_estandar(self, soup) -> List[ClubTecnico]:
        """Método alternativo: extraer de tabla estándar"""
        clubes = []
        
        try:
            tablas = soup.find_all('table', class_='items')
            
            for tabla in tablas:
                tbody = tabla.find('tbody')
                if not tbody:
                    continue
                
                # IMPORTANTE: Obtener TODAS las filas (sin filtro de clase)
                filas = tbody.find_all('tr')
                
                for fila in filas:
                    celdas = fila.find_all(['td', 'th'])
                    
                    if len(celdas) < 2:
                        continue
                    
                    try:
                        club_nombre = ""
                        pais = ""
                        periodo = ""
                        club_url = ""
                        fecha_inicio = ""
                        fecha_fin = ""
                        
                        # PASO 1: Buscar nombre del club Y verificar que sea "Entrenador" (no asistente, interino, etc.)
                        puesto = ""
                        
                        # PRIMERO: Buscar la celda que contiene "Entrenador" (tiene club + puesto)
                        for celda in celdas:
                            texto = celda.text.strip()
                            
                            # Buscar celdas con formato "ClubEntrenador" o "ClubEntrenador Asistente"
                            if 'Entrenador' in texto and len(texto) < 100:
                                # Dividir por "Entrenador" para separar club y puesto
                                idx = texto.index('Entrenador')
                                club_nombre = texto[:idx].strip()
                                puesto = texto[idx:].strip()
                                
                                # Buscar el link del club (puede estar en esta celda o en celdas cercanas)
                                link_club = celda.find('a', href=re.compile(r'/verein/\d+'))
                                if link_club:
                                    club_url = link_club.get('href', '')
                                
                                # Si no hay link en esta celda, buscar en la fila (puede estar en celda con imagen)
                                if not club_url:
                                    for c in celdas:
                                        l = c.find('a', href=re.compile(r'/verein/\d+'))
                                        if l:
                                            club_url = l.get('href', '')
                                            break
                                
                                break
                        
                        if not club_nombre:
                            continue
                        
                        # FILTRO IMPORTANTE: Solo considerar si es "Entrenador" (no asistente, interino, coordinador, etc.)
                        if not self._es_entrenador_principal(puesto):
                            continue
                        
                        # PASO 2: Extraer periodos (inicio y fin)
                        # Las celdas típicamente son: [0:imagen, 1:nombre+puesto, 2:inicio, 3:fin, 4:partidos, 5:PPP]
                        for i, celda in enumerate(celdas):
                            texto = celda.text.strip()
                            
                            # Buscar fecha de inicio (formato: "22/23 (01/01/2023)")
                            if '(' in texto and ')' in texto and not fecha_inicio:
                                fecha_inicio = texto
                            
                            # Buscar fecha de fin (formato: "24/25 (02/08/2024)" o "hasta 30/06/2026")
                            elif ('hasta' in texto.lower() or ')' in texto) and fecha_inicio and not fecha_fin:
                                fecha_fin = texto
                        
                        # Construir periodo unificado: "inicio - fin"
                        if fecha_inicio and fecha_fin:
                            periodo = f"{fecha_inicio} - {fecha_fin}"
                        elif fecha_inicio:
                            periodo = fecha_inicio
                        
                        # PASO 3: Obtener país del club
                        if club_url:
                            pais = self._obtener_pais_del_club(club_url)
                        
                        # PASO 4: Agregar club si es válido
                        if club_nombre and self._es_club_valido(club_nombre):
                            club = ClubTecnico(
                                club=self._normalizar_nombre_club(club_nombre),
                                pais=pais,
                                periodo=periodo
                            )
                            # Evitar duplicados
                            if not any(c.club == club.club and c.periodo == club.periodo for c in clubes):
                                clubes.append(club)
                    
                    except Exception:
                        continue
        
        except Exception:
            pass
        
        return clubes
    
    def _obtener_pais_del_club(self, club_url: str) -> str:
        """
        Obtiene el país de un club desde su página en Transfermarkt
        
        Args:
            club_url: URL relativa del club (ej: /deportivo-alaves/startseite/verein/1108)
        
        Returns:
            Nombre del país o cadena vacía
        """
        try:
            # Construir URL completa
            if not club_url.startswith('http'):
                club_url = f"{self.settings.TRANSFERMARKT_BASE_URL}{club_url}"
            
            # Hacer request con cache
            response = self.http_client.get(club_url, use_cache=True)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Buscar la bandera del país
            bandera = soup.find('img', class_='flaggenrahmen')
            if bandera:
                return bandera.get('title', '').strip()
        
        except Exception:
            pass
        
        return ""
    
    def _es_entrenador_principal(self, puesto: str) -> bool:
        """
        Verifica si el puesto es "Entrenador" principal (no asistente, interino, etc.)
        
        Args:
            puesto: Texto del puesto (ej: "Entrenador", "Entrenador Asistente", "Coordinador de la cantera")
        
        Returns:
            True si es entrenador principal, False si es otro rol
        """
        if not puesto:
            return False
        
        puesto_lower = puesto.lower()
        
        # Roles NO válidos (asistentes, interinos, coordinadores, etc.)
        roles_invalidos = [
            'asistente',
            'interino', 
            'coordinador',
            'ayudante',
            'auxiliar',
            'segundo',
            'analista',
            'preparador',
            'fisico',
            'físico',
            'cantera',
            'juveniles',
            'sub-',
            'reserva'
        ]
        
        # Si el puesto contiene algún rol inválido, rechazar
        if any(rol in puesto_lower for rol in roles_invalidos):
            return False
        
        # Si dice "entrenador" a secas, es válido
        if 'entrenador' in puesto_lower:
            return True
        
        # Si no dice "entrenador" en absoluto, rechazar
        return False
    
    def _es_club_valido(self, nombre: str) -> bool:
        """Valida que sea un nombre de club real"""
        invalidos = [
            'sin club', 'fin de carrera', 'retirado', 'libre',
            'agente libre', 'sin equipo', 'selección', 'nacional'
        ]
        
        nombre_lower = nombre.lower()
        return not any(inv in nombre_lower for inv in invalidos)
    
    def _normalizar_nombre_club(self, nombre: str) -> str:
        """Normaliza el nombre del club"""
        # Remover espacios extras
        nombre = ' '.join(nombre.split())
        return nombre.strip()
