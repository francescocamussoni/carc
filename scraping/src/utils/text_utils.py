"""
Utilidades para procesamiento de texto
"""

import re


class TextUtils:
    """Utilidades estáticas para procesamiento de texto"""
    
    @staticmethod
    def limpiar_nombre_archivo(nombre: str) -> str:
        """
        Limpia un nombre para usarlo como nombre de archivo
        
        Args:
            nombre: Nombre del jugador
        
        Returns:
            Nombre limpio para usar como archivo
        
        Examples:
            >>> TextUtils.limpiar_nombre_archivo("Germán Herrera")
            'german_herrera'
        """
        # Remover acentos y caracteres especiales
        nombre_limpio = nombre.lower()
        nombre_limpio = re.sub(r'[áàäâã]', 'a', nombre_limpio)
        nombre_limpio = re.sub(r'[éèëê]', 'e', nombre_limpio)
        nombre_limpio = re.sub(r'[íìïî]', 'i', nombre_limpio)
        nombre_limpio = re.sub(r'[óòöôõ]', 'o', nombre_limpio)
        nombre_limpio = re.sub(r'[úùüû]', 'u', nombre_limpio)
        nombre_limpio = re.sub(r'[ñ]', 'n', nombre_limpio)
        # Reemplazar espacios y caracteres especiales por guiones
        nombre_limpio = re.sub(r'[^a-z0-9]+', '_', nombre_limpio)
        # Remover guiones al inicio/final
        nombre_limpio = nombre_limpio.strip('_')
        return nombre_limpio
    
    @staticmethod
    def extraer_numero(texto: str) -> int:
        """
        Extrae el primer número de un texto
        
        Args:
            texto: Texto que contiene números
        
        Returns:
            Número extraído o 0 si no se encuentra
        
        Examples:
            >>> TextUtils.extraer_numero("348 partidos")
            348
        """
        numeros = ''.join(filter(str.isdigit, texto))
        return int(numeros) if numeros else 0
