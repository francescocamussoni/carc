# 🔧 Scraping - Rosario Central

Pipeline automatizado con 6 scrapers + índice optimizado para obtener datos de jugadores, técnicos y clubes desde Transfermarkt.

> **[← Volver al README principal](../README.md)**

---

## 📚 Índice

- [Instalación](#-instalación)
- [🚀 Pipeline Orquestado](#-pipeline-orquestado-nuevo)
- [Scrapers Disponibles](#-scrapers-disponibles)
  - [1. Jugadores](#1-jugadores)
  - [2. Técnicos](#2-técnicos)
  - [3. Logos de Clubes](#3-logos-de-clubes)
  - [4. Goles Detallados](#4-goles-detallados-opcional)
  - [5. Técnicos-Jugadores](#5-técnicos-jugadores-opcional)
  - [6. Índice Club-Posición](#6-índice-club-posición-nuevo)
- [Estructura de Datos](#-estructura-de-datos)
- [Configuración](#-configuración)

---

## 🛠️ Instalación

**Con uv** (recomendado - 10x más rápido):
```bash
cd scraping
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv pip install -r requirements.txt
```

**Con pip** (alternativa):
```bash
cd scraping
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## 🚀 Pipeline Orquestado (NUEVO)

**Ejecuta todos los scrapers automáticamente en el orden correcto:**

```bash
python scripts/run_pipeline.py
```

**Opciones:**
1. **Pipeline completo** - Jugadores + Técnicos + Logos + Índice + Opcionales (~45-60 min)
2. **Solo esencial** - Jugadores + Técnicos + Logos + Índice (~35-45 min)
3. **Solo jugadores** (~30-45 min)
4. **Solo técnicos** (~3-5 min)
5. **Solo logos** (~5-10 min)
6. **Solo índice** (~10-30 seg)

**Características:**
- ✅ **Ejecución paralela** (jugadores + técnicos simultáneamente)
- ✅ **Respeta dependencias** (logos espera a jugadores/técnicos, índice al final)
- ✅ **Auto-confirmación** (sin intervención manual)
- ✅ **Índice optimizado** (búsqueda O(1) por club y posición)
- ✅ **Resumen detallado** con tiempos
- ✅ **Scraping incremental** (continúa desde donde quedó)

---

## 🎯 Scrapers Disponibles

### 1. Jugadores

**Obtiene:** Jugadores históricos de Rosario Central con estadísticas completas.

**Ejecutar:**
```bash
python scripts/run_jugadores.py  # Renombrado desde run_scraper.py
```

**Output:** `data/output/rosario_central_jugadores.json`

**Incluye:**
- Nombre, nacionalidad, posición
- Foto de perfil
- Historia de clubes
- Estadísticas por torneo (partidos, goles, minutos, tarjetas)

**Ejemplo:**
```json
{
  "jugadores": [
    {
      "nombre": "Marco Ruben",
      "posicion": "Delantero centro",
      "partidos": 123,
      "clubes_historia": [...],
      "goles_por_torneo": [...]
    }
  ]
}
```

---

### 2. Técnicos

**Obtiene:** Todos los técnicos que dirigieron Rosario Central.

**Ejecutar:**
```bash
python scripts/run_tecnicos.py
```

**Output:** `data/output/rosario_central_tecnicos.json`

**Incluye:**
- Nombre, nacionalidad, foto
- Periodo(s) en Rosario Central
- Historia de clubes dirigidos
- Partidos dirigidos

**Ejemplo:**
```json
{
  "tecnicos": {
    "Eduardo Coudet": {
      "nacionalidad": "Argentina",
      "periodo_rosario": "01/01/2015 - 31/12/2016",
      "partidos_dirigidos": 81,
      "clubes_historia": [...]
    }
  }
}
```

---

### 3. Logos de Clubes (NUEVO)

**Obtiene:** Logos de todos los clubes donde jugaron/dirigieron jugadores/técnicos de Central.

**Ejecutar:**
```bash
python scripts/run_equipos.py
```

**Output:** `data/images/clubes/{pais}/{club}.png`

**Características:**
- ✅ Usa URLs directas del historial de jugadores/técnicos
- ✅ **Garantiza consistencia**: Nombres de clubes = Nombres de archivos
- ✅ Organizado por país (argentina/, italia/, españa/, etc.)
- ✅ ~300 clubes únicos
- ✅ Descarga paralela (5 workers)

**Ejemplo:**
```
data/images/clubes/
├── argentina/
│   ├── boca_juniors.png
│   ├── desamparados.png  # ✅ Ahora funciona
│   └── river_plate.png
├── italia/
│   ├── inter.png
│   └── juventus.png
└── ...
```

---

### 4. Goles Detallados (OPCIONAL)

**Output:** `data/output/rosario_central_tecnicos_jugadores.json`

**Incluye:**
- Jugadores por técnico y competencia
- Apariciones, goles, asistencias
- Resumen de jugadores más dirigidos

**Ejemplo:**
```json
{
  "tecnicos": {
    "Eduardo Coudet": {
      "jugadores_por_torneo": {
        "Liga Profesional": {
          "jugadores": [
            {
              "nombre": "Marco Ruben",
              "apariciones": 45,
              "goles": 15
            }
          ]
        }
      }
    }
  }
}
```

---

**Obtiene:** Información detallada de cada gol marcado por jugadores de Central.

**Ejecutar:**
```bash
python scripts/run_goles_detallados.py
```

**Output:** `data/output/rosario_central_goles_detallados.json`

**Incluye:**
- Rival, competición, fecha
- Minuto del gol
- Tipo de gol (cabeza, pie derecho, penal, etc.)
- Asistencia
- Resultado del partido

**Ejemplo:**
```json
{
  "goles": [
    {
      "jugador_nombre": "Marco Ruben",
      "rival": "Boca Juniors",
      "competicion": "Liga Profesional",
      "fecha": "2021-10-15",
      "minuto": "67",
      "tipo_gol": "Pie derecho",
      "de_penal": false,
      "asistencia": "Damián Martínez"
    }
  ]
}
```

---

### 5. Técnicos-Jugadores (OPCIONAL)

**Obtiene:** Jugadores dirigidos por cada técnico con estadísticas por competencia.

**Ejecutar:**
```bash
python scripts/run_tecnicos_jugadores.py
```

**Output:** `data/output/rosario_central_tecnicos_jugadores.json`

**Incluye:**
- Jugadores por técnico y competencia
- Apariciones, goles, asistencias
- Resumen de jugadores más dirigidos

---

### 6. Índice Club-Posición (NUEVO)

**Genera:** Índice optimizado para búsquedas rápidas de jugadores por club y posición.

**Ejecutar:**
```bash
python scripts/generar_indice_club_posicion.py
```

**Output:** `data/output/club_posicion_index.json`

**Características:**
- ✅ **Búsqueda O(1)** vs O(N*M) en datos originales
- ✅ ~856 clubes indexados
- ✅ ~1,600 jugadores distribuidos por club y posición
- ✅ Usado para pistas inteligentes y revelación de jugadores
- ✅ **Tiempo:** 10-30 segundos

**Estructura:**
```json
{
  "Rosario Central": {
    "DEL": [
      {
        "nombre": "Marco",
        "apellido": "Ruben",
        "posicion_principal": "DEL",
        "clubes_historia": [...],
        "image_profile": "data/images/jugadores/marco_ruben.jpg"
      }
    ],
    "MC": [...],
    "DC": [...]
  },
  "Boca Juniors": {...},
  "River Plate": {...}
}
```

**Integración:**
- **Backend:** Usa este índice para `obtenerPista()` y `revelarJugadorAleatorio()`
- **Pipeline:** Se ejecuta automáticamente después de jugadores/técnicos

---

## 📊 Estructura de Datos

### Output Files

```
data/
├── output/
│   ├── rosario_central_jugadores.json           # ~1,600 jugadores
│   ├── rosario_central_tecnicos.json            # ~65 técnicos
│   ├── club_posicion_index.json                 # Índice optimizado (NUEVO)
│   ├── rosario_central_tecnicos_jugadores.json  # Relaciones (opcional)
│   └── rosario_central_goles_detallados.json    # Goles (opcional)
└── images/
    ├── jugadores/   # ~1,600 fotos
    ├── tecnicos/    # ~65 fotos
    ├── clubes/      # ~300 logos
    │   ├── argentina/
    │   ├── italia/
    │   ├── españa/
    │   └── ...
    └── otras/       # Imágenes personalizadas (NUEVO)
        ├── ruben.jpg (84KB)
        ├── di_maria.jpg (60KB)
        ├── bauza.webp (27KB)
        ├── palma.webp (32KB)
        ├── miguel.png (339KB)
        └── petaco.avif (118KB)
```

### Relaciones

```python
# Unir jugadores con goles
jugadores = json.load('jugadores.json')['jugadores']
goles = json.load('goles_detallados.json')['goles']

for gol in goles:
    jugador = next(j for j in jugadores if j['nombre'] == gol['jugador_nombre'])
    print(f"{jugador['posicion']} marcó vs {gol['rival']}")

# Unir técnicos con jugadores
tecnicos = json.load('tecnicos.json')['tecnicos']
tec_jug = json.load('tecnicos_jugadores.json')['tecnicos']

for tec_nombre, data in tec_jug.items():
    partidos = tecnicos[tec_nombre]['partidos_dirigidos']
    jugadores_totales = len(data['resumen_general'])
    print(f"{tec_nombre}: {partidos} partidos, {jugadores_totales} jugadores")
```

---

## ⚙️ Configuración

**Archivo:** `src/config/settings.py`

```python
# Filtro de jugadores
MIN_PARTIDOS = 2

# Paralelización
MAX_WORKERS = 4
BATCH_SAVE_SIZE = 5

# Delays (evitar rate limiting)
DELAY_ENTRE_JUGADORES = (0.3, 0.8)  # segundos
DELAY_ENTRE_PAGINAS = (1, 2)
```

---

## 🚀 Performance

| Scraper | Cantidad | Tiempo (paralelo) |
|---------|----------|-------------------|
| **Pipeline Completo** | Todo | **~45-60 min** |
| **Pipeline Esencial** | Sin opcionales | **~35-45 min** |
| Jugadores | ~1,600 | ~30-45 min |
| Técnicos | ~65 | ~3-5 min |
| Logos de Clubes | ~300 | ~5-10 min |
| **Índice Club-Posición** | 856 clubes | **~10-30 seg** |
| Goles Detallados (opcional) | ~200 | ~7-10 min |
| Técnicos-Jugadores (opcional) | 65 | ~5-8 min |

**Optimizaciones:**
- ✅ **Orquestación inteligente** (pipeline automatizado)
- ✅ **Ejecución paralela** (jugadores + técnicos simultáneos)
- ✅ **Índice optimizado** (búsqueda O(1) vs O(N*M))
- ✅ **URLs directas** (logos desde historial, sin búsqueda)
- ✅ **Normalización consistente** (nombres = archivos)
- ✅ Paralelización (4-5 workers por scraper)
- ✅ Session pooling (keep-alive)
- ✅ Caché HTTP
- ✅ Scraping incremental (skip ya procesados)
- ✅ Retry con backoff exponencial
- ✅ Limpieza automática (números de camiseta, caracteres especiales)

---

## 🔧 Uso Avanzado

### Solo testing (pocos registros)

```bash
# Editar script y agregar límite
python scripts/run_scraper.py  # Pregunta cuántos jugadores
```

### Actualizar datos existentes

```bash
# Re-ejecutar cualquier scraper
# Automáticamente detecta y actualiza solo nuevos
python scripts/run_scraper.py
```

### Scraping sin paralelización

```python
# En el script, cambiar:
scraper.scrape(paralelo=False)  # Más lento pero más seguro
```

---

## 🐛 Troubleshooting

### Error: Rate limiting
**Solución:** Aumentar delays en `settings.py`

### Error: No se descarga imagen
**Solución:** Normal. Algunas imágenes no existen en Transfermarkt.

### Datos incompletos
**Solución:** Transfermarkt tiene datos desde ~2005. Jugadores antiguos pueden tener gaps.

---

## 📖 Documentación Adicional

- **[Backend API](../backend/README.md)** - Consume estos datos
- **[Frontend](../frontend/README.md)** - Muestra los juegos
- **[README Principal](../README.md)** - Overview del proyecto

---

**Versión:** 3.5  
**Performance:** 4-5x más rápido que v1, con pipeline automatizado + índice optimizado  
**Total datos:** ~2,000 imágenes + 5 JSON files (incluyendo índice)  
**Scrapers:** 6 scrapers + 1 procesador de índice  
**Última actualización:** 2026-03-04
