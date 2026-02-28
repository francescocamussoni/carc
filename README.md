# 🔵⚪ Rosario Central - Scrapers de Datos

Suite de scrapers **optimizados y paralelos** para obtener información completa de Rosario Central desde Transfermarkt:

1. **Scraper de Jugadores:** Información completa de jugadores históricos
2. **Scraper de Goles Detallados:** Todos los goles con información detallada (rival, competición, fecha, tipo, etc.)
3. **Scraper de Técnicos:** Todos los entrenadores que dirigieron el club con estadísticas completas

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![Performance](https://img.shields.io/badge/Performance-4x%20faster-green.svg)](OPTIMIZACIONES.md)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-success.svg)]()

---

## 📊 Datos Recopilados

Para cada jugador que haya jugado más de N partidos (configurable), el scraper obtiene:

### ✅ Información Básica
- **Nombre completo**
- **Nacionalidad**
- **Posición específica** (ej: Lateral izquierdo, Mediocentro defensivo)
- **Partidos totales** jugados en Rosario Central

### ✅ Multimedia
- **Foto de perfil** en alta calidad (descargada localmente)

### ✅ Carrera Profesional
- **Historia completa de clubes** (todos los equipos donde jugó)
- **País de cada club**
- **Período** en cada club

### ✅ Estadísticas por Torneo
Para cada torneo jugado en Rosario Central:
- **Temporada** (ej: 2023/24)
- **Competición** (ej: Liga Profesional, Copa Argentina, Sudamericana)
- **Partidos jugados**
- **Goles marcados**
- **Minutos jugados**
- **Tarjetas amarillas**
- **Dobles amarillas**
- **Tarjetas rojas**

---

## 🚀 Optimizaciones

**Versión 2.0** incluye optimizaciones significativas:

- ⚡ **Paralelización:** Procesa 4 jugadores simultáneamente
- 🔄 **Session Pooling:** Reutiliza conexiones HTTP (keep-alive)
- 📦 **Caché de HTTP:** Evita requests duplicados (speedup 100-1000x)
- 💾 **Batch Saving:** Guarda cada N jugadores (menos I/O)
- 🔒 **Thread-safe:** Operaciones seguras en paralelo
- ⚡ **Delays optimizados:** Reducidos gracias a paralelización

**Resultado: 4-5x más rápido que la versión anterior** 🎯

Ver detalles completos en [OPTIMIZACIONES.md](OPTIMIZACIONES.md)

---

## 🛠️ Instalación

### 1. Clonar repositorio
```bash
cd carc
```

### 2. Crear entorno virtual
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

---

## 🎯 Uso

### Ejecutar los scrapers

#### Scraper de Jugadores
```bash
# Activar entorno virtual
source venv/bin/activate

# Ejecutar scraper de jugadores
python scripts/run_scraper.py
```

#### Scraper de Goles Detallados
```bash
# Ejecutar scraper de goles detallados
python scripts/run_goles_detallados.py
```

#### Scraper de Técnicos
```bash
# Ejecutar scraper de técnicos
python scripts/run_tecnicos.py
```

Ver documentación específica en [docs/TECNICOS.md](docs/TECNICOS.md)

### Configuración (opcional)
Editar `src/config/settings.py`:

```python
# Filtro de jugadores
MIN_PARTIDOS = 2  # Mínimo de partidos para incluir al jugador

# Paralelización
MAX_WORKERS = 4         # Número de threads paralelos
BATCH_SAVE_SIZE = 5     # Guardar cada N jugadores

# Delays (para evitar rate limiting)
DELAY_ENTRE_JUGADORES = (0.3, 0.8)  # segundos
DELAY_ENTRE_PAGINAS = (1, 2)        # segundos
```

---

## 📂 Estructura del Proyecto

```
carc/
├── src/
│   ├── config/           # Configuración centralizada
│   │   └── settings.py   # Settings (Singleton pattern)
│   ├── models/           # Modelos de datos
│   │   └── jugador.py    # Dataclass Jugador
│   ├── scrapers/         # Scrapers (Strategy pattern)
│   │   ├── base_scraper.py
│   │   └── transfermarkt_scraper.py  # Scraper optimizado
│   ├── services/         # Lógica de negocio (Service Layer)
│   │   ├── image_service.py         # Descarga de imágenes
│   │   ├── storage_service.py       # Guardado thread-safe
│   │   ├── club_history_service.py  # Historia de clubes
│   │   └── stats_service.py         # Estadísticas (goles + tarjetas)
│   └── utils/            # Utilidades
│       ├── http_client.py   # Cliente HTTP con retry + caché + session pooling
│       └── text_utils.py    # Limpieza de texto
├── scripts/
│   └── run_scraper.py    # Script principal
├── data/
│   ├── output/           # JSON y CSV generados
│   └── images/           # Fotos de jugadores
├── requirements.txt      # Dependencias
├── README.md            # Este archivo
└── OPTIMIZACIONES.md    # Detalles de optimizaciones
```

---

## 📄 Formato de Salida

### JSON (`data/output/rosario_central_jugadores.json`)
```json
{
  "fecha_scraping": "2026-02-27T10:30:00",
  "total_jugadores": 123,
  "filtro_minimo_partidos": 2,
  "jugadores": [
    {
      "nombre": "Marco Ruben",
      "nacionalidad": "Argentina",
      "posicion": "Delantero centro",
      "partidos": 123,
      "image_profile": "data/images/marco_ruben.jpg",
      "url_perfil": "/marco-ruben/profil/spieler/30825",
      "clubes_historia": [
        {
          "nombre": "Rosario Central",
          "pais": "Argentina",
          "periodo": "01/07/2020"
        },
        {
          "nombre": "Club Atlético Tigre",
          "pais": "Argentina",
          "periodo": "01/07/2019"
        }
      ],
      "goles_por_torneo": [
        {
          "temporada": "2024",
          "competicion": "Liga Profesional",
          "partidos": 17,
          "goles": 1,
          "minutos": 951,
          "amarillas": 6,
          "doble_amarillas": 0,
          "rojas": 0
        },
        {
          "temporada": "2021",
          "competicion": "Liga Profesional",
          "partidos": 19,
          "goles": 15,
          "minutos": 1672,
          "amarillas": 4,
          "doble_amarillas": 0,
          "rojas": 0
        }
      ],
      "tarjetas_por_torneo": [
        {
          "temporada": "2024",
          "competicion": "Liga Profesional",
          "amarillas": 6,
          "doble_amarillas": 0,
          "rojas": 0
        }
      ],
      "fuente": "Transfermarkt (Completo)"
    }
  ]
}
```

### CSV (`data/output/rosario_central_jugadores.csv`)
Versión simplificada sin arrays anidados, ideal para Excel/análisis básico.

### 👔 Técnicos (`data/output/rosario_central_tecnicos.json`)

```json
{
  "fecha_scraping": "2026-02-27T20:00:00",
  "total_tecnicos": 65,
  "tecnicos": {
    "Eduardo Coudet": {
      "url_perfil": "/eduardo-coudet/profil/trainer/38808",
      "nacionalidad": "",
      "image_profile": "data/images/tecnicos/eduardo_coudet.jpg",
      "periodo_rosario": "01/01/2015 - 31/12/2016",
      "partidos_dirigidos": 81,
      "clubes_historia": [
        {
          "club": "Deportivo Alavés",
          "pais": "España",
          "periodo": "24/25 (02/12/2024)"
        },
        {
          "club": "Clube Atlético Mineiro",
          "pais": "Brasil",
          "periodo": "22/23 (01/01/2023)"
        },
        {
          "club": "RC Celta de Vigo",
          "pais": "España",
          "periodo": "20/21 (12/11/2020)"
        }
      ],
      "estadisticas_por_torneo": []
    }
  }
}
```

**Nota**: `estadisticas_por_torneo` está vacío porque Transfermarkt no proporciona este desglose para técnicos (solo muestra total de partidos).

---

## 🔧 Arquitectura

El proyecto sigue principios **SOLID** y patrones de diseño:

- **Singleton:** `Settings` (configuración única)
- **Strategy:** `BaseScraper` → `TransfermarktScraper`
- **Dependency Injection:** Services inyectados en Scrapers
- **Service Layer:** Lógica de negocio separada
- **Repository Pattern:** `StorageService` abstrae persistencia

**Beneficios:**
- ✅ Fácil de extender (agregar nuevos scrapers o fuentes)
- ✅ Testeable (mock de services)
- ✅ Mantenible (separación de responsabilidades)
- ✅ Escalable (paralelización nativa)

---

## 📈 Performance

### Benchmark (500 jugadores)

| Versión | Tiempo | Speedup |
|---------|--------|---------|
| v1.0 (secuencial) | ~25 min | 1x |
| v2.0 (paralelo) | ~5 min | **5x** |

*Nota: Tiempos reales dependen de la conexión a internet y respuesta de Transfermarkt*

---

## 🛡️ Manejo de Errores

El scraper es **robusto** y maneja:

✅ **Retry automático:** Si Transfermarkt falla, reintenta con backoff exponencial  
✅ **Guardado incremental:** Cada N jugadores se guarda progreso  
✅ **Skip duplicados:** No procesa jugadores ya scrappeados  
✅ **Error isolation:** Si un jugador falla, continúa con el resto  
✅ **Flush final:** Garantiza que no se pierdan datos al finalizar  

---

## 🤝 Contribuir

### Agregar nuevo scraper
1. Crear clase que herede de `BaseScraper`
2. Implementar método `scrape()`
3. Registrar en `scripts/run_scraper.py`

### Agregar nueva estadística
1. Agregar campo en `models/jugador.py`
2. Crear método en service correspondiente
3. Actualizar `TransfermarktScraper` para extraer dato

---

## 📝 Notas

- **Rate limiting:** El scraper incluye delays aleatorios para evitar bloqueos
- **User-Agent:** Simula navegador real
- **Respeto a Transfermarkt:** Por favor, no abuses del scraper
- **Caché inteligente:** No hace requests duplicados innecesariamente

---

## 🐛 Troubleshooting

### El scraper se detiene
- Verifica tu conexión a internet
- Aumenta `DELAY_ENTRE_JUGADORES` si Transfermarkt bloquea

### No encuentra jugadores
- Verifica que `TRANSFERMARKT_REKORDSPIELER_URL` sea correcta
- Revisa si Transfermarkt cambió su HTML

### Imágenes no se descargan
- Verifica permisos de escritura en `data/images/`
- Aumenta timeout en `http_client.py`

---

## 📞 Contacto

Para preguntas o sugerencias, abre un issue en el repositorio.

---

## 📜 Licencia

Este proyecto es para uso educativo y personal. Respeta los términos de servicio de Transfermarkt.

---

**Última actualización:** 2026-02-27  
**Versión:** 2.0 (Optimizada)  
**Autor:** Francesco Camussoni
