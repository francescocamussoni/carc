# 📊 Scraper de Jugadores Dirigidos por Técnicos

## 🎯 Objetivo

Este módulo obtiene información detallada de todos los jugadores que cada técnico dirigió en Rosario Central, organizados por temporada.

## 📁 Estructura del Proyecto

```
carc/
├── src/
│   ├── models/
│   │   └── jugador_tecnico.py          # Modelos: JugadorBajoTecnico, JugadoresPorTorneo, JugadoresTecnico
│   ├── services/
│   │   └── tecnico_jugadores_service.py # Servicio de extracción de jugadores
│   └── scrapers/
│       └── tecnico_jugadores_scraper.py # Scraper paralelizado
├── scripts/
│   └── run_tecnicos_jugadores.py        # Script principal
├── data/
│   └── output/
│       └── rosario_central_tecnicos_jugadores.json  # Salida JSON
└── docs/
    └── TECNICOS_JUGADORES.md            # Esta documentación
```

## 📊 Datos Recopilados

Para cada técnico que dirigió Rosario Central, se recopila:

### Resumen General (jugadores_mas_dirigidos)
- **Top 20 jugadores** más dirigidos por el técnico (todas las temporadas)
- **Total de apariciones**: Suma de partidos en todas las temporadas
- **Total de goles**: Suma de goles en todas las temporadas
- **Total de asistencias**: Suma de asistencias en todas las temporadas
- **Temporadas**: Cantidad de temporadas bajo ese técnico

### Por Torneo Específico
- **Torneo**: Nombre real del torneo (ej: "Copa Libertadores", "Liga Profesional", "Copa Argentina")
- **Temporada**: Año en que se jugó ese torneo
- **Total jugadores**: Cantidad de jugadores dirigidos en ese torneo

### Por Jugador (en cada torneo)
- **Nombre**: Nombre completo del jugador
- **Nacionalidad**: País de origen
- **Posición**: Posición detallada (ej: "Lateral izquierdo", "Mediocentro ofensivo")
- **Apariciones**: Partidos jugados bajo ese técnico en ese torneo
- **Goles**: Goles anotados en ese torneo
- **Asistencias**: Asistencias realizadas en ese torneo
- **Minutos**: Total de minutos jugados en ese torneo
- **URL de perfil**: Enlace al perfil del jugador en Transfermarkt

## 🚀 Uso

### Instalación

```bash
cd carc
source venv/bin/activate
pip install -r requirements.txt
```

### Ejecución

```bash
# Scraping de todos los técnicos (recomendado)
python scripts/run_tecnicos_jugadores.py

# Scraping de N técnicos (para testing)
python scripts/run_tecnicos_jugadores.py
# Luego seleccionar opción 2 y especificar cantidad
```

### Tiempo Estimado
- **Por técnico**: 2-5 segundos (depende de cuántos torneos dirigió)
- **Total (43 técnicos)**: ~5-8 minutos
- **Nota**: El scraper ahora extrae torneos específicos (Copa Libertadores, Liga Profesional, etc.) en lugar de temporadas genéricas

## 📄 Formato del JSON

```json
{
  "fecha_scraping": "2026-02-28T15:37:00",
  "total_tecnicos": 25,
  "total_torneos": 94,
  "total_jugadores_unicos": 451,
  "descripcion": "Jugadores dirigidos por cada técnico en Rosario Central, agrupados por torneo específico",
  "tecnicos": {
    "Miguel Ángel Russo": {
      "url_perfil": "/miguel-angel-russo/profil/trainer/2738",
      "total_torneos": 26,
      "jugadores_mas_dirigidos": [
        {
          "nombre": "Agustín Sández",
          "total_apariciones": 35,
          "total_goles": 2,
          "total_asistencias": 1,
          "total_minutos": 3030,
          "temporadas": 2
        },
        {
          "nombre": "Jorge Broun",
          "total_apariciones": 34,
          "total_goles": 0,
          "total_asistencias": 0,
          "total_minutos": 3060,
          "temporadas": 2
        },
        {
          "nombre": "Franco Ibarra",
          "total_apariciones": 33,
          "total_goles": 1,
          "total_asistencias": 2,
          "total_minutos": 2632,
          "temporadas": 2
        }
      ],
      "torneos": [
        {
          "torneo": "Copa Libertadores",
          "temporada": "2023",
          "total_jugadores": 25,
          "jugadores": [
            {
              "nombre": "Jorge Broun",
              "nacionalidad": "Argentina",
              "posicion": "Portero",
              "apariciones": 15,
              "goles": 0,
              "asistencias": 0,
              "minutos": 1350,
              "url_perfil": "https://www.transfermarkt.es/jorge-broun/profil/spieler/55150"
            },
            {
              "nombre": "Ignacio Malcorra",
              "nacionalidad": "Argentina",
              "posicion": "Mediocentro ofensivo",
              "apariciones": 15,
              "goles": 3,
              "asistencias": 1,
              "minutos": 1334,
              "url_perfil": "https://www.transfermarkt.es/ignacio-malcorra/profil/spieler/87518"
            }
          ]
        },
        {
          "torneo": "Liga Profesional de Fútbol (- 23/24)",
          "temporada": "2023",
          "total_jugadores": 25,
          "jugadores": [...]
        },
        {
          "torneo": "Copa Argentina",
          "temporada": "2022",
          "total_jugadores": 25,
          "jugadores": [...]
        }
      ]
    },
    "Ariel Holan": {
      "url_perfil": "/ariel-holan/profil/trainer/23127",
      "total_torneos": 1,
      "jugadores_mas_dirigidos": [
        {
          "nombre": "Agustín Sández",
          "total_apariciones": 35,
          "total_goles": 2,
          "total_asistencias": 5,
          "temporadas": 1
        }
      ],
      "torneos": [...]
    }
  }
}
```

## 🔍 Consultas Útiles con jq

```bash
# Ver todos los técnicos
cat data/output/rosario_central_tecnicos_jugadores.json | jq '.tecnicos | keys'

# Ver resumen completo de un técnico
jq '.tecnicos["Miguel Ángel Russo"]' data/output/rosario_central_tecnicos_jugadores.json

# Ver SOLO el top de jugadores más dirigidos por un técnico
jq '.tecnicos["Miguel Ángel Russo"].jugadores_mas_dirigidos' data/output/rosario_central_tecnicos_jugadores.json

# Ver temporadas dirigidas por un técnico
jq '.tecnicos["Miguel Ángel Russo"].torneos | map({torneo, temporada, total_jugadores})' data/output/rosario_central_tecnicos_jugadores.json

# Top 10 jugadores por apariciones bajo un técnico (temporada 2023)
jq '.tecnicos["Miguel Ángel Russo"].torneos[] | select(.temporada=="2023") | .jugadores | sort_by(.apariciones) | reverse | .[0:10] | .[] | {nombre, apariciones, goles, asistencias}' data/output/rosario_central_tecnicos_jugadores.json

# Jugador con más partidos dirigidos por Russo (todas las temporadas)
jq '.tecnicos["Miguel Ángel Russo"].jugadores_mas_dirigidos[0]' data/output/rosario_central_tecnicos_jugadores.json

# Técnicos con más temporadas dirigidas
jq '.tecnicos | to_entries | sort_by(.value.total_torneos) | reverse | .[0:10] | .[] | {tecnico: .key, temporadas: .value.total_torneos}' data/output/rosario_central_tecnicos_jugadores.json

# Todos los técnicos con sus jugadores más dirigidos (top 3 de cada uno)
jq '.tecnicos | to_entries | map({tecnico: .key, top_jugadores: .value.jugadores_mas_dirigidos[0:3]})' data/output/rosario_central_tecnicos_jugadores.json

# Contar total de jugadores únicos en todo el dataset
jq '.total_jugadores_unicos' data/output/rosario_central_tecnicos_jugadores.json

# Buscar en qué temporadas un jugador específico jugó bajo un técnico
jq '.tecnicos["Miguel Ángel Russo"].torneos[] | select(.jugadores[].nombre == "Jorge Broun") | {temporada, jugador: .jugadores[] | select(.nombre == "Jorge Broun")}' data/output/rosario_central_tecnicos_jugadores.json
```

## ⚙️ Arquitectura Técnica

### Modelos de Datos (`src/models/jugador_tecnico.py`)

- **`JugadorBajoTecnico`**: Representa un jugador con sus estadísticas bajo un técnico
- **`JugadoresPorTorneo`**: Agrupa jugadores de un torneo específico
- **`JugadoresTecnico`**: Estructura completa de jugadores por técnico

### Servicio de Extracción (`src/services/tecnico_jugadores_service.py`)

- **`obtener_jugadores_por_tecnico()`**: Obtiene todos los jugadores de un técnico
- **`_obtener_temporadas_en_central()`**: Identifica las temporadas del técnico en Central
- **`_obtener_torneos_de_temporada()`**: Extrae jugadores de una temporada
- **`_extraer_jugadores_de_tabla()`**: Parsea la tabla HTML de jugadores

### Scraper (`src/scrapers/tecnico_jugadores_scraper.py`)

- **Procesamiento paralelo**: Hasta 10 técnicos simultáneos
- **Guardado incremental**: Guarda progreso cada 5 técnicos
- **Manejo de errores**: Retry automático con exponential backoff
- **Thread-safe**: Operaciones seguras en entorno multi-thread

## 🔗 Fuente de Datos

Los datos se obtienen de [Transfermarkt.es](https://www.transfermarkt.es), específicamente de la página de "Jugadores utilizados" (`eingesetzteSpieler`) de cada técnico.

### Ejemplo de URL
```
https://www.transfermarkt.es/miguel-angel-russo/eingesetzteSpieler/trainer/2738/plus/0?saison_id=2022&verein_id=1418
```

Parámetros:
- `saison_id`: Año de la temporada (ej: 2022)
- `verein_id`: ID del club (1418 = Rosario Central)

## 📊 Estadísticas Generadas

El scraper proporciona estadísticas automáticas:
- **Total de técnicos** con jugadores
- **Total de torneos/temporadas** dirigidos
- **Total de jugadores únicos** en todos los técnicos
- **Top 10 técnicos** por número de temporadas

## ⚠️ Consideraciones

### Limitaciones
- Los datos están limitados a lo disponible en Transfermarkt
- No todas las temporadas históricas pueden tener información completa
- Las estadísticas son agregadas por temporada, no por torneo individual

### Rendimiento
- **Paralelización**: 10 workers concurrentes
- **Delay entre requests**: 0.3-0.8 segundos
- **Reintentos**: Hasta 3 intentos por error HTTP
- **Caché HTTP**: Reutilización de conexiones

## 🔄 Scraping Incremental

El scraper es incremental y reanudable:
- Carga técnicos ya procesados desde el JSON
- Salta técnicos que ya tienen jugadores
- Guarda progreso periódicamente
- Puede interrumpirse y reanudarse sin pérdida de datos

## 🆘 Troubleshooting

### No se encuentran temporadas para un técnico
- Verificar que el técnico tenga períodos en Rosario Central en el JSON de técnicos base
- Algunos técnicos interinos o con períodos muy cortos pueden no tener datos completos

### Error 404 en URLs
- Verificar que la URL del perfil del técnico sea correcta
- Algunos técnicos muy antiguos pueden no tener datos en Transfermarkt

### Jugadores con datos vacíos
- Revisar el parsing de la tabla HTML en `_extraer_jugadores_de_tabla()`
- Transfermarkt puede haber cambiado la estructura de sus páginas

## 📚 Recursos Adicionales

- [Documentación de Técnicos](./TECNICOS.md)
- [README Principal](../README.md)
- [Transfermarkt - Rosario Central](https://www.transfermarkt.es/rosario-central/startseite/verein/1418)
