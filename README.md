# ⚽🔵⚪ FutFactos - Rosario Central

Plataforma completa de trivias de fútbol basada en datos reales de Rosario Central.

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18-61dafb.svg)](https://reactjs.org/)

---

## 🎯 ¿Qué es esto?

Una aplicación web **full-stack** tipo [FutFactos.com](http://futfactos.com/) con 3 juegos de trivia:

1. **🇦🇷 Trayectoria Nacional** - Adivina el jugador por clubes argentinos
2. **🌎 Trayectoria Internacional** - Adivina el jugador por clubes extranjeros  
3. **⚽ Órbita del Día** - Identifica jugadores dirigidos por un técnico

---

## 🏗️ Estructura del Proyecto

```
carc/
├── backend/         # API REST (FastAPI)
├── frontend/        # App React (Vite)
├── scraping/        # Scrapers de Transfermarkt
│   └── data/        # Datos e imágenes
├── start.sh         # Script para iniciar todo
└── README.md        # Este archivo
```

### 📚 Documentación por Módulo

- **[Backend API](backend/README.md)** - FastAPI con 6 endpoints
- **[Frontend](frontend/README.md)** - React + Vite con 3 juegos
- **[Scraping](scraping/README.md)** - 4 scrapers optimizados

---

## 🚀 Inicio Rápido

### 1️⃣ Instalar dependencias

**Opción A: Setup automático** (recomendado)
```bash
./setup.sh
```

**Opción B: Manual con uv** (rápido ⚡)
```bash
# Backend
cd backend
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv pip install -r requirements.txt
cd ..

# Frontend
cd frontend
npm install
cd ..
```

**Instalar uv** (si no lo tienes):
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2️⃣ Ejecutar

**Opción A: Automático** (recomendado)
```bash
./start.sh
```

**Opción B: Manual**

Terminal 1 - Backend:
```bash
cd backend && python run.py
```

Terminal 2 - Frontend:
```bash
cd frontend && npm run dev
```

### 3️⃣ Abrir en navegador

- **App:** http://localhost:3000
- **API Docs:** http://localhost:8000/docs

---

## 🎮 Juegos Implementados

### 🇦🇷 Trayectoria Nacional
Adivina el jugador por su trayectoria en clubes argentinos.
- 5 vidas ❤️
- Clubes se revelan con errores
- Pistas progresivas

### 🌎 Trayectoria Internacional
Adivina el jugador por clubes del exterior.
- Misma mecánica que Nacional
- Enfocado en clubes internacionales

### ⚽ Órbita del Día
Identifica jugadores dirigidos por un técnico.
- Timer de 120 segundos ⏱️
- Múltiples jugadores para adivinar
- 3 modos: más minutos/goles/apariciones

---

## 📊 Datos Disponibles

| Tipo | Cantidad | Ubicación |
|------|----------|-----------|
| Jugadores | 451 | `scraping/data/output/rosario_central_jugadores.json` |
| Técnicos | 65 | `scraping/data/output/rosario_central_tecnicos.json` |
| Relaciones | 65 técnicos | `scraping/data/output/rosario_central_tecnicos_jugadores.json` |
| Goles | Miles | `scraping/data/output/rosario_central_goles_detallados.json` |
| Imágenes | 1,184 | `scraping/data/images/` |

**Generar datos nuevos:** Ver [Scraping README](scraping/README.md)

---

## 🏗️ Arquitectura

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│  Frontend   │─────▶│  Backend API │─────▶│  JSON Data  │
│  React      │◀─────│  FastAPI     │◀─────│  (scraping) │
└─────────────┘      └──────────────┘      └─────────────┘
```

**Flujo:**
1. Frontend solicita juego del día → Backend
2. Backend genera juego (determinístico por fecha) → Lee JSONs
3. Usuario adivina → Backend valida (fuzzy matching)
4. Backend retorna resultado → Frontend muestra feedback

---

## 🔧 Tecnologías

### Backend
- **FastAPI** - API REST
- **Pydantic** - Validación de datos
- **SQLite** (futuro) - Base de datos

### Frontend
- **React 18** - UI
- **Vite** - Build tool
- **React Router** - Navegación
- **Axios** - HTTP client

### Scraping
- **BeautifulSoup4** - Parsing HTML
- **Requests** - HTTP con retry + caché
- **ThreadPoolExecutor** - Paralelización (4 workers)

---

## 📝 Ejemplos de Uso

### Backend API

```bash
# Obtener juego del día
curl http://localhost:8000/api/v1/games/trayectoria-nacional

# Verificar respuesta
curl -X POST http://localhost:8000/api/v1/games/verify \
  -H "Content-Type: application/json" \
  -d '{"game_id": "trayectoria_nacional_20260228", "game_type": "trayectoria_nacional", "respuesta": "Marco Ruben"}'
```

### Frontend

```javascript
// Obtener juego
const game = await gamesAPI.getTrayectoriaNacional()

// Verificar respuesta
const result = await gamesAPI.verifyGuess(gameId, gameType, "Marco Ruben")
console.log(result.correcto) // true/false
```

### Scraping

```bash
# Obtener jugadores
cd scraping && python scripts/run_scraper.py

# Obtener técnicos
python scripts/run_tecnicos.py
```

---

## 🚢 Deploy

### Backend
```bash
# Railway, Fly.io, o similar
cd backend
railway up  # o fly deploy
```

### Frontend
```bash
# Vercel, Netlify
cd frontend
npm run build
vercel --prod
```

---

## 🤝 Contribuir

### Agregar nuevo juego

1. **Backend:** Endpoint en `backend/app/api/v1/endpoints/games.py`
2. **Service:** Lógica en `backend/app/services/game_generator.py`
3. **Frontend:** Página en `frontend/src/pages/NuevoJuego.jsx`
4. **Ruta:** Agregar en `frontend/src/App.jsx`

### Agregar nuevo scraper

1. Ver estructura en `scraping/src/scrapers/`
2. Seguir patrón de `transfermarkt_scraper.py`
3. Documentar en `scraping/README.md`

---

## 🐛 Troubleshooting

### Backend no conecta con datos
**Solución:** Verificar paths en `backend/app/core/config.py`:
```python
JUGADORES_JSON_PATH = "../scraping/data/output/rosario_central_jugadores.json"
```

### Frontend no carga imágenes
**Solución:** Backend debe servir static files desde `scraping/data/images/`

### Puerto en uso
```bash
# Matar procesos
lsof -ti :8000 | xargs kill -9  # Backend
lsof -ti :3000 | xargs kill -9  # Frontend
```

---

## 📖 Documentación Completa

| Módulo | README | Descripción |
|--------|--------|-------------|
| **Proyecto** | [README.md](README.md) | Este archivo |
| **Backend** | [backend/README.md](backend/README.md) | API REST, endpoints, schemas |
| **Frontend** | [frontend/README.md](frontend/README.md) | React app, componentes, estilos |
| **Scraping** | [scraping/README.md](scraping/README.md) | 4 scrapers, datos, performance |

---

## 📊 Estadísticas

- **Líneas de código:** ~4,500
- **Archivos creados:** ~40
- **Datos recopilados:** 451 jugadores, 65 técnicos, 1,184 imágenes
- **Tiempo de desarrollo:** 1 sesión
- **Performance:** Backend <100ms, Frontend 60fps

---

## 🎯 Roadmap (Futuro)

- [ ] Autenticación de usuarios
- [ ] Ranking global
- [ ] Más juegos (videos, kits, planteles)
- [ ] Base de datos PostgreSQL
- [ ] PWA (offline support)
- [ ] Tests unitarios

---

## 📄 Licencia

Uso educativo. Datos de Transfermarkt (respetar ToS).

---

<div align="center">

**Hecho con ❤️ para los canallas ⚽🔵⚪**

[Backend](backend/) • [Frontend](frontend/) • [Scraping](scraping/)

</div>

---

**Versión:** 1.0.0  
**Última actualización:** 2026-02-28
