# 🚀 Backend API - FutFactos Rosario Central

API REST con FastAPI para servir juegos de trivia de fútbol.

> **[← Volver al README principal](../README.md)**

---

## 🎯 Características

- ✅ **15 endpoints RESTful** (7 juegos + 8 servicios)
- ✅ Generación determinística de juegos (mismo juego/día para todos)
- ✅ **7 juegos implementados** (Trayectoria + Órbita + Clásico + 3 Equipos) 🆕
- ✅ **3 Modos de dificultad** (Potrero, Clásico, Hazaña)
- ✅ **Sistema de pistas inteligentes** (letra, posición, club)
- ✅ **Revelación automática de jugadores** (modo Potrero)
- ✅ **Sistema de formaciones dinámicas** (4-3-3, 4-2-3-1, 3-5-2, 3-4-1-2, etc.)
- ✅ **Juego del Clásico** con formaciones reales de Transfermarkt 🆕
- ✅ Selector de posición/jugador para múltiples opciones
- ✅ **Índice optimizado** club-posición (búsqueda O(1))
- ✅ Verificación con fuzzy matching + normalización de texto
- ✅ Servicio de imágenes estáticas (jugadores, técnicos, clubes, personalizadas)
- ✅ **Salto automático de clubes** sin jugadores disponibles
- ✅ Documentación automática (Swagger)
- ✅ CORS configurado
- ✅ **Docker-ready** para deployment 🆕

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

# Juego del Clásico (NUEVO) 🆕
GET  /api/v1/games/clasico                    # Clásico del día vs Newell's
POST /api/v1/games/clasico/verificar          # Verificar jugador del clásico
POST /api/v1/games/clasico/verificar-resultado # Verificar resultado del partido
GET  /api/v1/games/clasico/pista/{game_id}    # Pista para jugador del clásico
POST /api/v1/games/clasico/revelar/{game_id}  # Revelar jugador del clásico

# Juegos de Equipo
GET  /api/v1/games/equipo-nacional            # Arma equipo con argentinos
GET  /api/v1/games/equipo-europeo             # Arma equipo con europeos  
GET  /api/v1/games/equipo-latinoamericano     # Arma equipo con latinoamericanos

# Servicios Generales
POST /api/v1/games/verify                     # Verificar respuesta (juegos generales)
POST /api/v1/games/confirmar-posicion         # Confirmar posición (jugador polivalente)
POST /api/v1/games/confirmar-jugador          # Confirmar jugador (múltiples coincidencias)
GET  /api/v1/games/pista/{game_id}            # Obtener pista inteligente
POST /api/v1/games/revelar-jugador/{game_id}  # Revelar jugador aleatorio (modo Potrero)
GET  /api/v1/games/list                       # Listar juegos disponibles
```

### Static Files

```bash
GET /api/v1/static/jugadores/{nombre}.jpg      # Foto de jugador
GET /api/v1/static/tecnicos/{nombre}.jpg       # Foto de técnico
GET /api/v1/static/clubes/{pais}/{nombre}.png  # Logo de club (organizado por país)
GET /api/v1/static/otras/{nombre}              # Imágenes personalizadas (Rubén, Di María, etc.)
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

### Obtener pista inteligente

```bash
curl http://localhost:8000/api/v1/games/pista/equipo_nacional_20260304
```

**Response:**
```json
{
  "letra_apellido": "R",
  "posicion_principal": "DEL",
  "otro_club": "Dynamo Kyiv"
}
```

### Revelar jugador aleatorio

```bash
curl -X POST http://localhost:8000/api/v1/games/revelar-jugador/equipo_nacional_20260304
```

**Response:**
```json
{
  "success": true,
  "jugador_revelado": {
    "nombre": "Marco",
    "apellido": "Ruben",
    "posicion": "DEL",
    "image_url": "/api/v1/static/jugadores/marco_ruben.jpg"
  },
  "posicion_asignada": "DEL",
  "nuevo_club": {...}
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
CLUB_POSICION_INDEX_PATH = "../scraping/data/output/club_posicion_index.json"  # NUEVO
```

**Índice Optimizado:**

El archivo `club_posicion_index.json` organiza jugadores por club y posición para búsquedas O(1):

```json
{
  "Rosario Central": {
    "DEL": [{"nombre": "Marco", "apellido": "Ruben", ...}],
    "MC": [...]
  },
  "River Plate": {...}
}
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

### 🐳 Docker (Recomendado) 🆕

```bash
# Build imagen
docker build -t futfactos-backend .

# Run container
docker run -p 8000:8000 \
  -v $(pwd)/../scraping/data:/app/scraping/data \
  futfactos-backend

# O usar docker-compose (ver DEPLOYMENT.md)
```

**Dockerfile incluido** con:
- Multi-stage build (optimizado)
- Python 3.9 slim
- Health checks
- Non-root user
- Volumes para datos estáticos

### ☁️ AWS (Con CI/CD)

Ver **[DEPLOYMENT.md](../DEPLOYMENT.md)** para deployment completo con Terraform + GitHub Actions.

**Incluye:**
- EC2 t4g.micro (ARM, Free Tier)
- Docker en EC2
- Auto-deploy en push a `main`
- Ultra low-cost ($0-3/mes)

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
- **[Deployment AWS](../DEPLOYMENT.md)** - Infraestructura y CI/CD 🆕

---

**FastAPI:** 0.109.0  
**Python:** 3.9+  
**Docker:** Multi-stage build incluido  
**Última actualización:** 2026-03-07  
**Endpoints:** 15 (7 juegos + 8 servicios)  
**Juegos:** 7 (Nacional, Internacional, Órbita, Clásico, 3 Equipos)
