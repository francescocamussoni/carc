"""
Scraper para Transfermarkt con paralelización optimizada
"""

import time
import random
import re
from typing import List, Tuple, Optional
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
from .base_scraper import BaseScraper
from ..models import Jugador


class TransfermarktScraper(BaseScraper):
    """
    Scraper específico para Transfermarkt con paralelización
    Obtiene datos completos incluyendo partidos de todos los torneos y posiciones específicas
    """
    
    def get_source_name(self) -> str:
        return "Transfermarkt (Completo)"
    
    def scrape(self) -> List[Jugador]:
        """
        Scrappea datos COMPLETOS de Transfermarkt con PAGINACIÓN y PARALELIZACIÓN
        
        Proceso en 2 fases:
        1. Fase de recolección: Obtener datos básicos de todas las páginas
        2. Fase de procesamiento: Procesar jugadores en paralelo
        
        Returns:
            Lista de jugadores scrappeados
        """
        print("🔍 Scrapeando Transfermarkt (DATOS COMPLETOS)")
        print("   ✅ Partidos de TODOS los torneos (liga + copas + internacionales)")
        print("   ✅ Posiciones específicas de cada jugador")
        print("   ✅ Fotos de perfil en alta calidad")
        print("   ✅ Historia completa de clubes (carrera profesional)")
        print("   ✅ Estadísticas por torneo (goles, amarillas, rojas)")
        print("   ✅ Recorriendo TODAS las páginas disponibles")
        print(f"   ⚡ Paralelización: {self.settings.MAX_WORKERS} workers")
        print(f"   💾 Batch saving: cada {self.settings.BATCH_SAVE_SIZE} jugadores")
        print()
        
        # ============================================
        # FASE 1: RECOLECCIÓN DE DATOS BÁSICOS
        # ============================================
        print("📋 FASE 1: Recolectando jugadores de todas las páginas...")
        jugadores_a_procesar = self._recolectar_jugadores_basicos()
        
        if not jugadores_a_procesar:
            print("⚠️  No se encontraron jugadores nuevos para procesar")
            return self.storage.jugadores
        
        print(f"✅ {len(jugadores_a_procesar)} jugadores nuevos para procesar\n")
        
        # ============================================
        # FASE 2: PROCESAMIENTO EN PARALELO
        # ============================================
        print(f"⚡ FASE 2: Procesando {len(jugadores_a_procesar)} jugadores en paralelo...")
        jugadores_procesados = self._procesar_jugadores_paralelo(jugadores_a_procesar)
        
        # Flush any pending saves
        self.storage.flush_pending()
        
        # Resumen final
        print(f"\n✅ Transfermarkt completado:")
        print(f"   - Total en archivo: {len(self.storage.jugadores)} jugadores")
        print(f"   - Nuevos en esta ejecución: {len(jugadores_procesados)} jugadores")
        
        return self.storage.jugadores
    
    def _recolectar_jugadores_basicos(self) -> List[Tuple]:
        """
        Recolecta datos básicos de jugadores de todas las páginas
        
        Returns:
            Lista de tuplas (nombre, nacionalidad, partidos, url_perfil, numero)
        """
        jugadores_basicos = []
        pagina = 1
        jugador_count = 0
        
        while pagina <= self.settings.MAX_PAGINAS:
            try:
                print(f"  📄 Página {pagina}...", end=' ')
                
                # Construir URL con paginación
                url = self._construir_url_pagina(pagina)
                
                # Obtener HTML
                response = self.http_client.get(url)
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Buscar tabla de jugadores
                tabla = soup.find('table', {'class': 'items'})
                
                if not tabla:
                    print("⏹️  No hay más páginas")
                    break
                
                # Procesar filas
                filas = tabla.find_all('tr')[1:]  # Saltar encabezado
                
                if not filas:
                    print("⏹️  Sin jugadores")
                    break
                
                nuevos_en_pagina = 0
                
                for fila in filas:
                    try:
                        # Extraer datos básicos de la fila
                        datos_basicos = self._extraer_datos_fila(fila)
                        
                        if not datos_basicos:
                            continue
                        
                        nombre, nacionalidad, partidos, url_perfil = datos_basicos
                        jugador_count += 1
                        
                        # Verificar si ya existe
                        if self.storage.jugador_existe(nombre):
                            continue
                        
                        # Filtrar por mínimo de partidos
                        if partidos < self.settings.MIN_PARTIDOS:
                            continue
                        
                        # Agregar a la lista para procesar
                        jugadores_basicos.append((
                            nombre,
                            nacionalidad,
                            partidos,
                            url_perfil,
                            jugador_count
                        ))
                        nuevos_en_pagina += 1
                    
                    except Exception:
                        continue
                
                print(f"✅ {nuevos_en_pagina} nuevos")
                
                pagina += 1
                # Delay entre páginas
                time.sleep(random.uniform(*self.settings.DELAY_ENTRE_PAGINAS))
            
            except Exception as e:
                print(f"\n   ❌ Error en página {pagina}: {e}")
                break
        
        return jugadores_basicos
    
    def _procesar_jugadores_paralelo(self, jugadores_basicos: List[Tuple]) -> List[Jugador]:
        """
        Procesa jugadores en paralelo usando ThreadPoolExecutor
        
        Args:
            jugadores_basicos: Lista de tuplas con datos básicos
        
        Returns:
            Lista de jugadores procesados
        """
        jugadores_procesados = []
        total = len(jugadores_basicos)
        
        with ThreadPoolExecutor(max_workers=self.settings.MAX_WORKERS) as executor:
            # Enviar todos los jugadores al pool
            future_to_jugador = {
                executor.submit(self._procesar_jugador, *jugador_data): jugador_data
                for jugador_data in jugadores_basicos
            }
            
            # Procesar resultados conforme se completan
            completed = 0
            for future in as_completed(future_to_jugador):
                completed += 1
                jugador_data = future_to_jugador[future]
                nombre = jugador_data[0]
                numero = jugador_data[4]
                
                try:
                    jugador = future.result()
                    if jugador:
                        # Agregar en modo batch (thread-safe)
                        self.storage.agregar_jugador(jugador, batch_mode=True)
                        jugadores_procesados.append(jugador)
                        
                        # Progress
                        porcentaje = (completed / total) * 100
                        print(f"  [{completed:>3}/{total}] ({porcentaje:>5.1f}%) [{numero:>3}] {nombre[:30]:<30} ✅")
                    else:
                        print(f"  [{completed:>3}/{total}] [{numero:>3}] {nombre[:30]:<30} ⚠️  Error")
                
                except Exception as e:
                    print(f"  [{completed:>3}/{total}] [{numero:>3}] {nombre[:30]:<30} ❌ {str(e)[:30]}")
                    continue
        
        return jugadores_procesados
    
    def _procesar_jugador(self, nombre: str, nacionalidad: str, partidos: int, 
                          url_perfil: str, numero: int) -> Optional[Jugador]:
        """
        Procesa un jugador individual (obtiene datos completos del perfil)
        Esta función se ejecuta en paralelo
        
        Args:
            nombre: Nombre del jugador
            nacionalidad: Nacionalidad del jugador
            partidos: Partidos jugados
            url_perfil: URL del perfil
            numero: Número de jugador (para logging)
        
        Returns:
            Jugador con todos los datos o None si falla
        """
        try:
            # Small random delay to avoid hammering the server
            time.sleep(random.uniform(0.1, 0.3))
            
            # Obtener datos completos del perfil
            posicion_principal, posiciones_lista, nombre_pila, apellido, imagen_perfil, clubes_historia, tarjetas_por_torneo, goles_por_torneo = self._obtener_datos_completos_perfil(
                url_perfil, 
                nombre
            )
            
            # Crear jugador
            jugador = Jugador(
                nombre=nombre,
                nacionalidad=nacionalidad,
                posicion=posicion_principal,
                partidos=partidos,
                nombre_pila=nombre_pila,
                apellido=apellido,
                posiciones=posiciones_lista,
                image_profile=imagen_perfil,
                clubes_historia=clubes_historia,
                tarjetas_por_torneo=tarjetas_por_torneo,
                goles_por_torneo=goles_por_torneo,
                url_perfil=url_perfil,
                fuente=self.get_source_name()
            )
            
            return jugador
        
        except Exception as e:
            # Propagar la excepción para que se capture en el future
            raise Exception(f"Error procesando {nombre}: {str(e)}")
    
    def _construir_url_pagina(self, pagina: int) -> str:
        """Construye la URL para una página específica"""
        return f"{self.settings.TRANSFERMARKT_REKORDSPIELER_URL}/page/{pagina}"
    
    def _extraer_datos_fila(self, fila) -> Optional[Tuple[str, str, int, str]]:
        """Extrae datos básicos de una fila de la tabla"""
        try:
            celdas = fila.find_all(['td', 'th'])
            if len(celdas) < 8:
                return None
            
            # Celda 3: Nombre
            nombre = celdas[3].text.strip()
            
            # Celda 5: Nacionalidad (bandera)
            nacionalidades = celdas[5].find_all('img')
            if nacionalidades:
                nacionalidad = nacionalidades[0].get('title', 'Desconocida')
            else:
                nacionalidad = 'Argentina'
            
            # Celda 7: Partidos jugados
            partidos_text = celdas[7].text.strip()
            partidos = int(''.join(filter(str.isdigit, partidos_text))) if partidos_text else 0
            
            # URL del perfil
            link = celdas[3].find('a', href=True)
            url_perfil = link['href'] if link else None
            
            if not url_perfil:
                return None
            
            return (nombre, nacionalidad, partidos, url_perfil)
        
        except Exception:
            return None
    
    def _obtener_datos_completos_perfil(self, url_perfil: str, nombre_jugador: str) -> Tuple[str, Optional[List[str]], Optional[str], Optional[str], Optional[str], Optional[List], Optional[List], Optional[List]]:
        """Obtiene TODOS los datos del jugador desde su perfil"""
        try:
            url_completa = f"{self.settings.TRANSFERMARKT_BASE_URL}{url_perfil}"
            response = self.http_client.get(url_completa, use_cache=True)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extraer nombre y apellido
            nombre_pila, apellido = self._extraer_nombre_apellido(soup, nombre_jugador)
            
            # Extraer posiciones (principal + secundarias)
            posicion_principal, posiciones_lista = self._extraer_posiciones(soup)
            
            # Usar nombre completo limpio para imagen
            nombre_completo_limpio = f"{nombre_pila}_{apellido}".replace(" ", "_") if nombre_pila and apellido else nombre_jugador
            
            # Extraer y descargar imagen
            imagen_perfil = self._extraer_y_descargar_imagen(soup, nombre_completo_limpio)
            
            # Extraer clubes
            clubes_historia = self.club_history.obtener_clubes_jugador(url_perfil, nombre_jugador)
            if clubes_historia:
                clubes_historia = [c if isinstance(c, dict) else c.to_dict() for c in clubes_historia]
            
            # Extraer estadísticas completas (goles + tarjetas + partidos por torneo)
            goles_por_torneo = self.stats_service.obtener_goles_rosario_central(url_perfil, nombre_jugador)
            
            # Mantener tarjetas_por_torneo por compatibilidad
            tarjetas_por_torneo = [
                {
                    'temporada': t['temporada'],
                    'competicion': t['competicion'],
                    'amarillas': t['amarillas'],
                    'doble_amarillas': t['doble_amarillas'],
                    'rojas': t['rojas']
                }
                for t in goles_por_torneo
                if t.get('amarillas', 0) > 0 or t.get('doble_amarillas', 0) > 0 or t.get('rojas', 0) > 0
            ]
            
            return (posicion_principal, posiciones_lista, nombre_pila, apellido, imagen_perfil, clubes_historia, tarjetas_por_torneo, goles_por_torneo)
        
        except Exception as e:
            return ("Desconocida", ["Desconocida"], None, None, None, None, None, None)
    
    def _extraer_nombre_apellido(self, soup, nombre_fallback: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Extrae el nombre y apellido del jugador desde el HTML del perfil
        
        En Transfermarkt, el formato es:
        <h1>Nombre <strong>Apellido</strong></h1>
        
        Ejemplo: Ángel <strong>Di María</strong>
        
        Args:
            soup: BeautifulSoup object del perfil
            nombre_fallback: Nombre completo de fallback si no se puede extraer
            
        Returns:
            Tupla (nombre_pila, apellido)
        """
        try:
            # Buscar el h1 con la clase data-header__headline-wrapper
            h1 = soup.find('h1', class_='data-header__headline-wrapper')
            
            if h1:
                # Extraer el apellido del <strong>
                strong_tag = h1.find('strong')
                if strong_tag:
                    apellido = strong_tag.text.strip()
                    
                    # Extraer el nombre (todo el texto antes del <strong>)
                    # Crear una copia del h1 y eliminar el strong para obtener solo el nombre
                    nombre_pila = h1.get_text(strip=True).replace(apellido, '').strip()
                    
                    if nombre_pila and apellido:
                        return (nombre_pila, apellido)
            
            # Si no se pudo extraer, intentar separar por espacios como fallback
            partes = nombre_fallback.strip().split()
            if len(partes) >= 2:
                # Asumir que la última parte es el apellido
                apellido = partes[-1]
                nombre_pila = ' '.join(partes[:-1])
                return (nombre_pila, apellido)
            
            # Si todo falla, devolver el nombre completo como nombre
            return (nombre_fallback, nombre_fallback)
            
        except Exception:
            # En caso de error, usar el nombre completo como fallback
            partes = nombre_fallback.strip().split()
            if len(partes) >= 2:
                return (' '.join(partes[:-1]), partes[-1])
            return (nombre_fallback, nombre_fallback)
    
    def _extraer_posiciones(self, soup) -> Tuple[str, List[str]]:
        """
        Extrae todas las posiciones del jugador desde el HTML del perfil
        
        Transfermarkt muestra:
        - Posición principal: <dt>Posición principal :</dt><dd>Extremo derecho</dd>
        - Posiciones secundarias: <dt>Posición secundaria:</dt><dd>Mediocentro ofensivo</dd><dd>Extremo izquierdo</dd>
        
        Returns:
            Tupla (posicion_principal, lista_de_todas_posiciones)
        """
        try:
            posiciones = []
            posicion_principal = "Desconocida"
            
            # Buscar en el contenedor detail-position
            detail_position = soup.find('div', class_='detail-position__box')
            
            if detail_position:
                # Buscar todas las definiciones de posiciones
                dls = detail_position.find_all('dl')
                
                for dl in dls:
                    dt = dl.find('dt', class_='detail-position__title')
                    if dt:
                        titulo = dt.text.strip()
                        
                        # Extraer las posiciones
                        dds = dl.find_all('dd', class_='detail-position__position')
                        
                        for dd in dds:
                            posicion = dd.text.strip()
                            if posicion:
                                posiciones.append(posicion)
                                
                                # Si es la posición principal, guardarla aparte
                                if 'principal' in titulo.lower() and not posicion_principal or posicion_principal == "Desconocida":
                                    posicion_principal = posicion
            
            # Si no se encontró ninguna posición con el método anterior, buscar en data-header
            if not posiciones:
                labels = soup.find_all('li', class_='data-header__label')
                for label in labels:
                    if 'Posición:' in label.text or 'Posicion:' in label.text:
                        content = label.find('span', class_='data-header__content')
                        if content:
                            posicion = content.text.strip()
                            posiciones.append(posicion)
                            posicion_principal = posicion
            
            # Si no se encontró nada, usar "Desconocida"
            if not posiciones:
                posiciones = ["Desconocida"]
                posicion_principal = "Desconocida"
            
            return (posicion_principal, posiciones)
            
        except Exception as e:
            return ("Desconocida", ["Desconocida"])
    
    def _extraer_y_descargar_imagen(self, soup, nombre_jugador: str) -> Optional[str]:
        """Extrae la URL de la imagen y la descarga"""
        try:
            imagen_tag = soup.find('img', class_='data-header__profile-image')
            if imagen_tag and imagen_tag.get('src'):
                url_imagen = imagen_tag['src']
                # Obtener versión de alta calidad
                url_imagen = url_imagen.replace('/small/', '/header/').replace('/medium/', '/header/')
                return self.image_service.descargar_imagen(url_imagen, nombre_jugador)
            return None
        except Exception:
            return None
