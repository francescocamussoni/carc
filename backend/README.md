# 🚀 Backend API - FutFactos Rosario Central

API REST con FastAPI para servir juegos de trivia de fútbol.

> **[← Volver al README principal](../README.md)**

---

## 🎯 Características

- ✅ 6 endpoints RESTful
- ✅ Generación determinística de juegos (mismo juego/día para todos)
- ✅ Verificación con fuzzy matching
- ✅ Servicio de imágenes estáticas
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
GET  /api/v1/games/trayectoria-nacional       # Juego trayectoria nacional
GET  /api/v1/games/trayectoria-internacional  # Juego trayectoria internacional  
GET  /api/v1/games/orbita                     # Juego órbita
POST /api/v1/games/verify                     # Verificar respuesta
GET  /api/v1/games/list                       # Listar juegos disponibles
```

### Static Files

```bash
GET /api/v1/static/jugadores/{nombre}.jpg  # Foto de jugador
GET /api/v1/static/tecnicos/{nombre}.jpg   # Foto de técnico
GET /api/v1/static/clubes/{nombre}.png     # Logo de club
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
