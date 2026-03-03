#!/usr/bin/env python3
"""
Pipeline orquestador para ejecutar todos los scrapers de Rosario Central
en el orden correcto respetando dependencias.

Dependencias:
  Nivel 1 (paralelo): run_jugadores.py + run_tecnicos.py
  Nivel 2 (final):    run_equipos.py (necesita URLs de nivel 1)
  Nivel 3 (opcional): run_goles_detallados.py + run_tecnicos_jugadores.py
"""

import sys
import subprocess
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Tuple, Optional


class Color:
    """Códigos de color para terminal"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class PipelineScraper:
    """
    Orquestador del pipeline de scraping
    """
    
    def __init__(self, base_path: Path):
        """
        Inicializa el pipeline
        
        Args:
            base_path: Path al directorio de scripts
        """
        self.base_path = base_path
        self.scripts = {
            'jugadores': 'run_jugadores.py',
            'tecnicos': 'run_tecnicos.py',
            'equipos': 'run_equipos.py',
            'goles': 'run_goles_detallados.py',
            'tecnicos_jugadores': 'run_tecnicos_jugadores.py',
            'indice': 'generar_indice_club_posicion.py'
        }
        
        self.tiempos = {}
        self.resultados = {}
    
    def print_banner(self):
        """Imprime el banner del pipeline"""
        print()
        print(Color.BOLD + "=" * 80)
        print("🚀 PIPELINE COMPLETO DE SCRAPING - ROSARIO CENTRAL")
        print("=" * 80 + Color.ENDC)
        print()
        print("Este pipeline ejecuta todos los scrapers en el orden correcto:")
        print()
        print(Color.OKBLUE + "  NIVEL 1 (Paralelo):" + Color.ENDC)
        print("    1️⃣  Jugadores históricos")
        print("    2️⃣  Técnicos/entrenadores")
        print()
        print(Color.OKBLUE + "  NIVEL 2 (Secuencial):" + Color.ENDC)
        print("    3️⃣  Logos de clubes (usa URLs de nivel 1)")
        print()
        print(Color.OKBLUE + "  NIVEL 3 (Opcional - Paralelo):" + Color.ENDC)
        print("    4️⃣  Goles detallados")
        print("    5️⃣  Jugadores por técnico")
        print()
        print(Color.OKBLUE + "  NIVEL 4 (Post-procesamiento):" + Color.ENDC)
        print("    6️⃣  Índice club-posición (optimización)")
        print()
    
    def _ejecutar_script(self, nombre: str, script: str, auto_confirmar: bool = True) -> Tuple[bool, Optional[float]]:
        """
        Ejecuta un script individual
        
        Args:
            nombre: Nombre descriptivo del script
            script: Nombre del archivo de script
            auto_confirmar: Si es True, responde 's' automáticamente
        
        Returns:
            Tupla (éxito, tiempo_ejecución)
        """
        print(f"\n{Color.OKCYAN}{'='*80}")
        print(f"▶️  Ejecutando: {nombre}")
        print(f"{'='*80}{Color.ENDC}\n")
        
        script_path = self.base_path / script
        
        if not script_path.exists():
            print(f"{Color.FAIL}❌ Error: Script no encontrado: {script_path}{Color.ENDC}")
            return (False, None)
        
        try:
            inicio = datetime.now()
            
            # Preparar el comando
            cmd = [sys.executable, str(script_path)]
            
            # Si auto-confirmar, pasar todas las respuestas necesarias
            if auto_confirmar:
                proceso = subprocess.Popen(
                    cmd,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    cwd=str(self.base_path)
                )
                
                # Enviar respuestas:
                # 1. 's' para confirmar
                # 2. Enter para aceptar opción por defecto (todos los registros)
                output, _ = proceso.communicate(input='s\n\n')
                print(output)
                
                exit_code = proceso.returncode
            else:
                # Ejecutar interactivamente
                exit_code = subprocess.call(cmd, cwd=str(self.base_path))
            
            fin = datetime.now()
            tiempo = (fin - inicio).total_seconds()
            
            if exit_code == 0:
                print(f"\n{Color.OKGREEN}✅ {nombre} completado en {tiempo:.1f}s{Color.ENDC}")
                return (True, tiempo)
            else:
                print(f"\n{Color.FAIL}❌ {nombre} falló (código de salida: {exit_code}){Color.ENDC}")
                return (False, tiempo)
        
        except Exception as e:
            print(f"\n{Color.FAIL}❌ Error ejecutando {nombre}: {e}{Color.ENDC}")
            return (False, None)
    
    def ejecutar_nivel_1_paralelo(self) -> bool:
        """
        Ejecuta jugadores y técnicos en paralelo
        
        Returns:
            True si ambos terminaron exitosamente
        """
        print(f"\n{Color.BOLD}{Color.OKBLUE}🔄 NIVEL 1: Ejecutando jugadores y técnicos en paralelo...{Color.ENDC}\n")
        
        with ThreadPoolExecutor(max_workers=2) as executor:
            # Enviar ambas tareas
            future_jugadores = executor.submit(
                self._ejecutar_script, 
                "Jugadores", 
                self.scripts['jugadores']
            )
            future_tecnicos = executor.submit(
                self._ejecutar_script, 
                "Técnicos", 
                self.scripts['tecnicos']
            )
            
            # Esperar resultados
            exito_jugadores, tiempo_jugadores = future_jugadores.result()
            exito_tecnicos, tiempo_tecnicos = future_tecnicos.result()
            
            self.resultados['jugadores'] = exito_jugadores
            self.resultados['tecnicos'] = exito_tecnicos
            self.tiempos['jugadores'] = tiempo_jugadores
            self.tiempos['tecnicos'] = tiempo_tecnicos
            
            return exito_jugadores and exito_tecnicos
    
    def ejecutar_nivel_2_secuencial(self) -> bool:
        """
        Ejecuta logos de clubes (necesita URLs de nivel 1)
        
        Returns:
            True si terminó exitosamente
        """
        print(f"\n{Color.BOLD}{Color.OKBLUE}🔄 NIVEL 2: Ejecutando logos de clubes...{Color.ENDC}\n")
        
        exito, tiempo = self._ejecutar_script(
            "Logos de Clubes", 
            self.scripts['equipos']
        )
        
        self.resultados['equipos'] = exito
        self.tiempos['equipos'] = tiempo
        
        return exito
    
    def ejecutar_nivel_3_paralelo(self) -> Tuple[bool, bool]:
        """
        Ejecuta goles detallados y técnicos-jugadores en paralelo
        
        Returns:
            Tupla (exito_goles, exito_tecnicos_jugadores)
        """
        print(f"\n{Color.BOLD}{Color.OKBLUE}🔄 NIVEL 3 (Opcional): Ejecutando datos detallados en paralelo...{Color.ENDC}\n")
        
        with ThreadPoolExecutor(max_workers=2) as executor:
            # Enviar ambas tareas
            future_goles = executor.submit(
                self._ejecutar_script, 
                "Goles Detallados", 
                self.scripts['goles']
            )
            future_tec_jug = executor.submit(
                self._ejecutar_script, 
                "Técnicos-Jugadores", 
                self.scripts['tecnicos_jugadores']
            )
            
            # Esperar resultados
            exito_goles, tiempo_goles = future_goles.result()
            exito_tec_jug, tiempo_tec_jug = future_tec_jug.result()
            
            self.resultados['goles'] = exito_goles
            self.resultados['tecnicos_jugadores'] = exito_tec_jug
            self.tiempos['goles'] = tiempo_goles
            self.tiempos['tecnicos_jugadores'] = tiempo_tec_jug
            
            return (exito_goles, exito_tec_jug)
    
    def print_resumen(self, inicio_total: datetime):
        """Imprime resumen de ejecución"""
        fin_total = datetime.now()
        tiempo_total = (fin_total - inicio_total).total_seconds()
        
        print(f"\n{Color.BOLD}{'='*80}")
        print("📊 RESUMEN DE EJECUCIÓN")
        print(f"{'='*80}{Color.ENDC}\n")
        
        print(f"{Color.BOLD}Resultados por script:{Color.ENDC}")
        for nombre, exito in self.resultados.items():
            tiempo = self.tiempos.get(nombre)
            icono = "✅" if exito else "❌"
            tiempo_str = f"({tiempo:.1f}s)" if tiempo else "(N/A)"
            print(f"  {icono} {nombre.replace('_', ' ').title():<25} {tiempo_str}")
        
        print(f"\n{Color.BOLD}Tiempo total:{Color.ENDC} {tiempo_total:.1f}s ({tiempo_total/60:.1f} min)")
        
        exitosos = sum(1 for e in self.resultados.values() if e)
        total = len(self.resultados)
        print(f"{Color.BOLD}Scripts exitosos:{Color.ENDC} {exitosos}/{total}")
        
        if exitosos == total:
            print(f"\n{Color.OKGREEN}{Color.BOLD}🎉 ¡Pipeline completado exitosamente!{Color.ENDC}")
        else:
            print(f"\n{Color.WARNING}{Color.BOLD}⚠️  Pipeline completado con errores{Color.ENDC}")
        
        print(f"\n{'='*80}\n")
    
    def ejecutar_pipeline_completo(self, incluir_opcionales: bool = True):
        """
        Ejecuta el pipeline completo
        
        Args:
            incluir_opcionales: Si es True, ejecuta nivel 3 (goles y técnicos-jugadores)
        """
        inicio_total = datetime.now()
        
        # Nivel 1: Jugadores y Técnicos (paralelo)
        if not self.ejecutar_nivel_1_paralelo():
            print(f"\n{Color.FAIL}❌ Error en Nivel 1. Abortando pipeline.{Color.ENDC}")
            self.print_resumen(inicio_total)
            return False
        
        # Nivel 2: Logos de clubes (necesita nivel 1)
        if not self.ejecutar_nivel_2_secuencial():
            print(f"\n{Color.WARNING}⚠️  Error en Nivel 2. Continuando con opcionales...{Color.ENDC}")
        
        # Nivel 3: Opcionales (paralelo)
        if incluir_opcionales:
            self.ejecutar_nivel_3_paralelo()
        
        # Nivel 4: Post-procesamiento (índice optimizado)
        self.ejecutar_nivel_4_indices()
        
        # Resumen
        self.print_resumen(inicio_total)
        
        return True
    
    def ejecutar_nivel_4_indices(self) -> bool:
        """
        Ejecuta generación de índices optimizados
        
        Returns:
            True si terminó exitosamente
        """
        print(f"\n{Color.BOLD}{Color.OKBLUE}🔄 NIVEL 4: Generando índices optimizados...{Color.ENDC}\n")
        
        exito, tiempo = self._ejecutar_script(
            "Índice Club-Posición",
            self.scripts['indice'],
            auto_confirmar=False  # No necesita confirmación
        )
        
        self.resultados['indice'] = exito
        self.tiempos['indice'] = tiempo
        
        return exito


def main():
    """Función principal"""
    try:
        # Path al directorio de scripts
        script_dir = Path(__file__).parent
        
        # Crear pipeline
        pipeline = PipelineScraper(script_dir)
        
        # Banner
        pipeline.print_banner()
        
        # Opciones
        print(Color.BOLD + "Opciones de ejecución:" + Color.ENDC)
        print("  1. Pipeline completo (jugadores + técnicos + logos + opcionales)")
        print("  2. Solo esencial (jugadores + técnicos + logos)")
        print("  3. Solo jugadores")
        print("  4. Solo técnicos")
        print("  5. Solo logos (requiere datos existentes)")
        print()
        
        opcion = input("Selecciona una opción (1-5) [1]: ").strip() or "1"
        print()
        
        inicio = datetime.now()
        
        if opcion == "1":
            # Pipeline completo
            pipeline.ejecutar_pipeline_completo(incluir_opcionales=True)
        
        elif opcion == "2":
            # Solo esencial
            pipeline.ejecutar_pipeline_completo(incluir_opcionales=False)
        
        elif opcion == "3":
            # Solo jugadores
            exito, tiempo = pipeline._ejecutar_script("Jugadores", pipeline.scripts['jugadores'], auto_confirmar=False)
            pipeline.resultados['jugadores'] = exito
            pipeline.tiempos['jugadores'] = tiempo
            pipeline.print_resumen(inicio)
        
        elif opcion == "4":
            # Solo técnicos
            exito, tiempo = pipeline._ejecutar_script("Técnicos", pipeline.scripts['tecnicos'], auto_confirmar=False)
            pipeline.resultados['tecnicos'] = exito
            pipeline.tiempos['tecnicos'] = tiempo
            pipeline.print_resumen(inicio)
        
        elif opcion == "5":
            # Solo logos
            exito, tiempo = pipeline._ejecutar_script("Logos de Clubes", pipeline.scripts['equipos'], auto_confirmar=False)
            pipeline.resultados['equipos'] = exito
            pipeline.tiempos['equipos'] = tiempo
            pipeline.print_resumen(inicio)
        
        else:
            print(f"{Color.FAIL}❌ Opción inválida{Color.ENDC}")
            return 1
        
        return 0
    
    except KeyboardInterrupt:
        print(f"\n\n{Color.WARNING}⚠️  Pipeline interrumpido por el usuario{Color.ENDC}")
        return 1
    
    except Exception as e:
        print(f"\n{Color.FAIL}❌ Error fatal: {e}{Color.ENDC}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
