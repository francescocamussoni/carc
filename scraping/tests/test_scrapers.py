"""
Tests unitarios para scrapers
"""

import unittest
from unittest.mock import Mock, patch
from src.models import Jugador
from src.config import Settings
from src.utils import TextUtils


class TestTextUtils(unittest.TestCase):
    """Tests para TextUtils"""
    
    def test_limpiar_nombre_archivo(self):
        """Test de limpieza de nombres"""
        self.assertEqual(TextUtils.limpiar_nombre_archivo("Germán Herrera"), "german_herrera")
        self.assertEqual(TextUtils.limpiar_nombre_archivo("José María López"), "jose_maria_lopez")
        self.assertEqual(TextUtils.limpiar_nombre_archivo("Ángel Di María"), "angel_di_maria")
    
    def test_extraer_numero(self):
        """Test de extracción de números"""
        self.assertEqual(TextUtils.extraer_numero("348 partidos"), 348)
        self.assertEqual(TextUtils.extraer_numero("No hay números"), 0)
        self.assertEqual(TextUtils.extraer_numero("123abc456"), 123456)


class TestJugador(unittest.TestCase):
    """Tests para el modelo Jugador"""
    
    def test_crear_jugador(self):
        """Test de creación de jugador"""
        jugador = Jugador(
            nombre="Paulo Ferrari",
            nacionalidad="Argentina",
            posicion="Lateral derecho",
            partidos=348
        )
        
        self.assertEqual(jugador.nombre, "Paulo Ferrari")
        self.assertEqual(jugador.partidos, 348)
        self.assertIsNone(jugador.image_profile)
    
    def test_to_dict(self):
        """Test de conversión a diccionario"""
        jugador = Jugador(
            nombre="Marco Ruben",
            nacionalidad="Argentina",
            posicion="Delantero centro",
            partidos=283
        )
        
        data = jugador.to_dict()
        self.assertEqual(data['nombre'], "Marco Ruben")
        self.assertEqual(data['partidos'], 283)
    
    def test_from_dict(self):
        """Test de creación desde diccionario"""
        data = {
            'nombre': 'Jorge Broun',
            'nacionalidad': 'Argentina',
            'posicion': 'Portero',
            'partidos': 274,
            'image_profile': None,
            'fuente': 'Transfermarkt'
        }
        
        jugador = Jugador.from_dict(data)
        self.assertEqual(jugador.nombre, "Jorge Broun")
        self.assertEqual(jugador.posicion, "Portero")


class TestSettings(unittest.TestCase):
    """Tests para Settings"""
    
    def test_singleton(self):
        """Test de patrón Singleton"""
        settings1 = Settings()
        settings2 = Settings()
        
        # Deben ser la misma instancia
        self.assertIs(settings1, settings2)
    
    def test_update(self):
        """Test de actualización de configuración"""
        settings = Settings()
        original_min = settings.MIN_PARTIDOS
        
        settings.update(MIN_PARTIDOS=5)
        self.assertEqual(settings.MIN_PARTIDOS, 5)
        
        # Restaurar
        settings.update(MIN_PARTIDOS=original_min)


if __name__ == '__main__':
    unittest.main()
