# 🚀 Backend API - FutFactos Rosario Central

API REST con FastAPI para servir juegos de trivia de fútbol.

> **[← Volver al README principal](../README.md)**

---

## 🎯 Características

- ✅ 9 endpoints RESTful (6 juegos + 3 servicios)
- ✅ Generación determinística de juegos (mismo juego/día para todos)
- ✅ 6 juegos implementados (Trayectoria + Órbita + Equipo)
- ✅ Sistema de formaciones dinámicas (4-3-3, 4-4-2, 3-5-2, 4-3-2-1)
- ✅ Selector de posición para jugadores polivalentes
- ✅ Verificación con fuzzy matching + normalización de texto
- ✅ Servicio de imágenes estáticas (jugadores, técnicos, clubes)
- ✅ Documentación automática (Swagger)
- ✅ CORS configurado

---

## 🛠️ Instalación

**Con uv** (recomendado - 10x más rápido):
```bash
cd backend
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv pip install -r requirements.txt
```

**Con pip** (alternativa):
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## 🚀 Ejecutar

```bash
python run.py
```

**URLs:**
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

---

## 📡 Endpoints

### Juegos del Día

```bash
# Juegos de Trayectoria
GET  /api/v1/games/trayectoria-nacional       # Adivina por clubes argentinos
GET  /api/v1/games/trayectoria-internacional  # Adivina por clubes extranjeros

# Juego Órbita
GET  /api/v1/games/orbita                     # Jugadores dirigidos por técnico

# Juegos de Equipo (NUEVO)
GET  /api/v1/games/equipo-nacional            # Arma equipo con argentinos
GET  /api/v1/games/equipo-europeo             # Arma equipo con europeos  
GET  /api/v1/games/equipo-latinoamericano     # Arma equipo con latinoamericanos

# Servicios
POST /api/v1/games/verify                     # Verificar respuesta
POST /api/v1/games/confirmar-posicion         # Confirmar posición de jugador (NUEVO)
GET  /api/v1/games/list                       # Listar juegos disponibles
```

### Static Files

```bash
GET /api/v1/static/jugadores/{nombre}.jpg      # Foto de jugador
GET /api/v1/static/tecnicos/{nombre}.jpg       # Foto de técnico
GET /api/v1/static/clubes/{pais}/{nombre}.png  # Logo de club (organizado por país)
```

---

## 📖 Ejemplos

### Obtener juego

```bash
curl http://localhost:8000/api/v1/games/trayectoria-nacional
```

**Response:**
```json
{
  "success": true,
  "game_type": "trayectoria_nacional",
  "game_id": "trayectoria_nacional_20260228",
  "data": {
    "jugador_oculto": {"nombre": "???"},
    "clubes_nacionales": [...],
    "pistas": ["Posición: Delantero"],
    "max_vidas": 5
  }
}
```

### Verificar respuesta

```bash
curl -X POST http://localhost:8000/api/v1/games/verify \
  -H "Content-Type: application/json" \
  -d '{
    "game_id": "trayectoria_nacional_20260228",
    "game_type": "trayectoria_nacional",
    "respuesta": "Marco Ruben"
  }'
```

**Response (correcto):**
```json
{
  "correcto": true,
  "mensaje": "¡Correcto! Era Marco Ruben",
  "jugador_revelado": {...},
  "game_over": true,
  "victoria": true
}
```

---

## 🏗️ Estructura

```
backend/
├── app/
│   ├── api/v1/              # Endpoints
│   │   └── endpoints/
│   │       └── games.py
│   ├── core/                # Configuración
│   │   └── config.py
│   ├── schemas/             # Pydantic models
│   │   └── game.py
│   ├── services/            # Lógica de juegos
│   │   ├── data_loader.py
│   │   └── game_generator.py
│   └── main.py              # FastAPI app
├── requirements.txt
└── run.py
```

---

## ⚙️ Configuración

**Archivo:** `app/core/config.py`

```python
API_V1_PREFIX = "/api/v1"
BACKEND_CORS_ORIGINS = ["http://localhost:3000"]

# Paths a datos (generados por scraping)
JUGADORES_JSON_PATH = "../scraping/data/output/rosario_central_jugadores.json"
TECNICOS_JSON_PATH = "../scraping/data/output/rosario_central_tecnicos.json"
```

---

## 🎲 Lógica de Juegos

Los juegos se generan **determinísticamente** por fecha:

```python
seed = int(date.today().strftime("%Y%m%d")) + hash(game_type) % 1000
random.seed(seed)
jugador = random.choice(candidatos)
```

**Resultado:** Todos los usuarios ven el mismo juego en un día dado.

---

## 🔍 Fuzzy Matching

Acepta respuestas aproximadas:

```python
guess = "marco ruben"
correct = "Marco Ruben"
# ✅ Match (similarity >= 0.8)

guess = "ruben"  
correct = "Marco Ruben"
# ✅ Match (substring)
```

---

## 📚 Documentación

- **[Swagger UI](http://localhost:8000/docs)** - Interactiva
- **[ReDoc](http://localhost:8000/redoc)** - Alternativa
- **[OpenAPI JSON](http://localhost:8000/api/v1/openapi.json)** - Spec

---

## 🚢 Deploy

### Railway

```bash
# Crear Procfile
echo "web: uvicorn app.main:app --host 0.0.0.0 --port \$PORT" > Procfile

# Deploy
railway up
```

### Fly.io

```bash
fly deploy
```

---

## 🔗 Enlaces

- **[README Principal](../README.md)** - Overview del proyecto
- **[Frontend](../frontend/README.md)** - Consume esta API
- **[Scraping](../scraping/README.md)** - Genera los datos

---

**FastAPI:** 0.109.0  
**Python:** 3.9+  
**Última actualización:** 2026-03-03
