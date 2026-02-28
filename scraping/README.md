# 🔧 Scraping - Rosario Central

Scrapers optimizados para obtener datos de jugadores y técnicos desde Transfermarkt.

> **[← Volver al README principal](../README.md)**

---

## 📚 Índice

- [Instalación](#-instalación)
- [Scrapers Disponibles](#-scrapers-disponibles)
  - [1. Jugadores](#1-jugadores)
  - [2. Técnicos](#2-técnicos)
  - [3. Técnicos-Jugadores](#3-técnicos-jugadores)
  - [4. Goles Detallados](#4-goles-detallados)
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

## 🎯 Scrapers Disponibles

### 1. Jugadores

**Obtiene:** Jugadores históricos de Rosario Central con estadísticas completas.

**Ejecutar:**
```bash
python scripts/run_scraper.py
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

### 3. Técnicos-Jugadores

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

### 4. Goles Detallados

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

## 📊 Estructura de Datos

### Output Files

```
data/
├── output/
│   ├── rosario_central_jugadores.json           # 451 jugadores
│   ├── rosario_central_tecnicos.json            # 65 técnicos
│   ├── rosario_central_tecnicos_jugadores.json  # Relaciones
│   └── rosario_central_goles_detallados.json    # Goles individuales
└── images/
    ├── jugadores/   # 451 fotos
    ├── tecnicos/    # 43 fotos
    └── clubes/      # 690 logos
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
| Jugadores | 451 | ~5-7 min |
| Técnicos | 65 | ~3-4 min |
| Técnicos-Jugadores | 65 técnicos | ~15-20 min |
| Goles Detallados | 100 jugadores | ~2-3 min |

**Optimizaciones:**
- ✅ Paralelización (4 workers)
- ✅ Session pooling (keep-alive)
- ✅ Caché HTTP
- ✅ Scraping incremental (skip ya procesados)
- ✅ Retry con backoff exponencial

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

**Versión:** 2.0  
**Performance:** 4-5x más rápido que v1  
**Total datos:** 1,184 imágenes + 4 JSON files
