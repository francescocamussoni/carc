# ⚽ Scraper de Goles Detallados

## 📋 Descripción

Este módulo scrapea información detallada de **todos los goles** marcados por jugadores de Rosario Central, extrayendo datos como:

- ✅ Rival contra el que marcó
- ✅ País del rival
- ✅ Competición y temporada
- ✅ Fecha del gol
- ✅ Minuto del gol
- ✅ Resultado del partido
- ✅ Tipo de gol (pie derecho, cabeza, penal, etc.)
- ✅ Asistencia (si disponible)

---

## 🏗️ Arquitectura

El módulo sigue la misma arquitectura del scraper principal:

```
carc/
├── src/
│   ├── models/
│   │   └── gol_detallado.py           # Modelo de datos
│   ├── services/
│   │   └── goles_detallados_service.py # Lógica de extracción
│   ├── scrapers/
│   │   └── goles_detallados_scraper.py # Orquestador
├── scripts/
│   └── run_goles_detallados.py         # Script principal
├── data/
│   └── output/
│       └── rosario_central_goles_detallados.json # Salida
```

**Principios aplicados:**
- ✅ Separación de responsabilidades (Service Layer)
- ✅ Modelos de datos con dataclasses
- ✅ Scraping incremental (skip duplicados)
- ✅ Paralelización con ThreadPoolExecutor
- ✅ Retry automático con backoff
- ✅ Session pooling para eficiencia

---

## 🚀 Uso

### Requisito Previo

Debe existir `rosario_central_jugadores.json` con los jugadores de Rosario Central:

```bash
# Si no lo tienes, ejecuta primero:
python scripts/run_scraper.py
```

### Ejecución

```bash
cd carc
source venv/bin/activate
python scripts/run_goles_detallados.py
```

El script es **interactivo** y te preguntará:
1. Si deseas continuar
2. Si quieres procesar todos los jugadores o limitar a N (para testing)

### Opciones Avanzadas

Puedes personalizar el scraping desde código:

```python
from src.scrapers.goles_detallados_scraper import GolesDetalladosScraper

scraper = GolesDetalladosScraper()

# Procesar solo 10 jugadores (testing)
goles = scraper.scrape(max_jugadores=10, paralelo=True)

# Procesar todos (producción)
goles = scraper.scrape(max_jugadores=None, paralelo=True)

# Procesamiento secuencial (más lento pero más seguro)
goles = scraper.scrape(paralelo=False)
```

---

## 📊 Formato de Salida

### JSON Structure

```json
{
  "fecha_scraping": "2026-02-27T15:30:00",
  "total_jugadores": 45,
  "total_goles": 234,
  "goles_por_jugador": {
    "Marco Ruben": 67,
    "Alan Marinelli": 23,
    ...
  },
  "goles": [
    {
      "jugador_nombre": "Marco Ruben",
      "jugador_url": "/marco-ruben/profil/spieler/30825",
      "rival": "Boca Juniors",
      "rival_pais": "Argentina",
      "competicion": "Liga Profesional",
      "temporada": "2021/22",
      "fecha": "2021-10-15",
      "minuto": "67",
      "resultado": "2-1",
      "tipo_gol": "Pie derecho",
      "de_penal": false,
      "asistencia": "Damián Martínez",
      "gol_numero": "2:1"
    },
    ...
  ]
}
```

### Campos del Gol

| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `jugador_nombre` | string | Nombre del jugador (clave primaria) | "Marco Ruben" |
| `jugador_url` | string | URL del perfil en Transfermarkt | "/marco-ruben/profil/spieler/30825" |
| `rival` | string | Equipo rival | "Boca Juniors" |
| `rival_pais` | string | País del rival | "Argentina" |
| `competicion` | string | Competición | "Liga Profesional" |
| `temporada` | string | Temporada | "2021/22" |
| `fecha` | string | Fecha (ISO format) | "2021-10-15" |
| `minuto` | string | Minuto del gol | "67" o "90+3" |
| `resultado` | string | Resultado final | "2-1" |
| `tipo_gol` | string | Tipo de gol | "Pie derecho", "Cabeza", etc. |
| `de_penal` | boolean | Si fue penal | true/false |
| `asistencia` | string | Jugador que asistió | "Damián Martínez" o null |
| `gol_numero` | string | Marcador cuando anotó | "2:1" |

---

## 🔗 Matcheo con Jugadores

El campo `jugador_nombre` es la **clave primaria** para unir con `rosario_central_jugadores.json`:

### Ejemplo en Python

```python
import json

# Cargar jugadores
with open('data/output/rosario_central_jugadores.json') as f:
    jugadores_data = json.load(f)
    jugadores = {j['nombre']: j for j in jugadores_data['jugadores']}

# Cargar goles
with open('data/output/rosario_central_goles_detallados.json') as f:
    goles_data = json.load(f)

# Matchear
for gol in goles_data['goles']:
    nombre = gol['jugador_nombre']
    if nombre in jugadores:
        jugador = jugadores[nombre]
        print(f"{nombre} ({jugador['posicion']}) marcó vs {gol['rival']}")
```

### Ejemplo en SQL (si importas a DB)

```sql
SELECT 
    j.nombre,
    j.posicion,
    j.nacionalidad,
    COUNT(g.rival) as total_goles,
    COUNT(DISTINCT g.rival) as rivales_diferentes
FROM jugadores j
LEFT JOIN goles_detallados g ON j.nombre = g.jugador_nombre
GROUP BY j.nombre, j.posicion, j.nacionalidad
ORDER BY total_goles DESC;
```

---

## 📈 Performance

### Tiempo de Ejecución

| Jugadores | Secuencial | Paralelo (4 workers) |
|-----------|-----------|---------------------|
| 10        | ~30-50s   | ~10-15s            |
| 50        | ~3-5 min  | ~1-2 min           |
| 100       | ~6-10 min | ~2-3 min           |
| 200       | ~12-20 min| ~4-6 min           |

**Factores que afectan:**
- Número de goles por jugador
- Velocidad de conexión a internet
- Response time de Transfermarkt

### Optimizaciones Aplicadas

- ✅ **Paralelización:** 4 workers simultáneos
- ✅ **Session pooling:** Reutiliza conexiones HTTP
- ✅ **Caché:** Evita requests duplicados
- ✅ **Scraping incremental:** Saltea jugadores ya procesados
- ✅ **Delays inteligentes:** Evita rate limiting

---

## 🔍 Análisis de Datos

### Top Goleadores

```python
from collections import Counter
import json

with open('data/output/rosario_central_goles_detallados.json') as f:
    data = json.load(f)

# Top 10 goleadores
goles_por_jugador = Counter(g['jugador_nombre'] for g in data['goles'])
for jugador, goles in goles_por_jugador.most_common(10):
    print(f"{jugador}: {goles} goles")
```

### Goles por Competición

```python
goles_por_comp = Counter(g['competicion'] for g in data['goles'])
for comp, goles in goles_por_comp.most_common(5):
    print(f"{comp}: {goles} goles")
```

### Goles de Penal

```python
penales = sum(1 for g in data['goles'] if g['de_penal'])
total = len(data['goles'])
print(f"Penales: {penales}/{total} ({penales/total*100:.1f}%)")
```

### Rivales más Goleados

```python
goles_por_rival = Counter(g['rival'] for g in data['goles'])
for rival, goles in goles_por_rival.most_common(10):
    print(f"{rival}: {goles} goles recibidos")
```

---

## 🛠️ Troubleshooting

### Error: "No se encontró rosario_central_jugadores.json"

**Solución:** Ejecuta primero el scraper principal:
```bash
python scripts/run_scraper.py
```

### Error: "Sin URL de perfil"

**Causa:** Algunos jugadores en el JSON no tienen `url_perfil`.

**Solución:** Estos jugadores se saltean automáticamente. Para corregir, re-scrappea con la última versión del scraper principal.

### Jugador sin goles

Es normal. Algunos jugadores (especialmente defensores y arqueros) pueden no tener goles registrados en Transfermarkt.

### Rate Limiting

Si Transfermarkt bloquea temporalmente:
1. El scraper tiene retry automático
2. Puedes aumentar delays en `settings.py`
3. Ejecuta con `paralelo=False` para ser más conservador

---

## 📝 Notas

- **Datos históricos:** Transfermarkt tiene goles desde aproximadamente 2005 en adelante para ligas argentinas.
- **Goles antiguos:** Jugadores que jugaron antes de 2005 pueden tener datos incompletos.
- **Actualización:** Re-ejecuta el script periódicamente para actualizar con nuevos goles.
- **Respeto a Transfermarkt:** No abuses del scraper. Los delays están configurados para ser respetuosos.

---

## 🤝 Contribuir

Si quieres agregar más datos (ej: tarjetas en cada gol, sustituciones), puedes extender:

1. **Modelo:** Agrega campos en `src/models/gol_detallado.py`
2. **Servicio:** Extrae datos en `src/services/goles_detallados_service.py`
3. **Documentación:** Actualiza este archivo

---

**Última actualización:** 2026-02-27  
**Versión:** 1.0  
**Autor:** Francesco Camussoni
