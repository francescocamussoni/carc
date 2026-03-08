# ⚽🔵⚪ FutFactos - Rosario Central

Plataforma completa de trivias de fútbol basada en datos reales de Rosario Central.

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18-61dafb.svg)](https://reactjs.org/)
[![AWS](https://img.shields.io/badge/AWS-Ready-orange.svg)](https://aws.amazon.com/)

---

## 🎯 ¿Qué es esto?

Una aplicación web **full-stack** tipo [FutFactos.com](http://futfactos.com/) con **7 juegos de trivia**:

1. **🇦🇷 Trayectoria Nacional** - Adivina el jugador por clubes argentinos
2. **🌎 Trayectoria Internacional** - Adivina el jugador por clubes extranjeros  
3. **⚽ Órbita del Día** - Identifica jugadores dirigidos por un técnico
4. **🔵⚪ Clásico del Día** - Adivina la formación titular de clásicos históricos vs Newell's 🆕
5. **🇦🇷 Equipo Nacional** - Arma el equipo titular con jugadores argentinos
6. **🌍 Equipo Europeo** - Arma el equipo titular con jugadores europeos
7. **🌎 Equipo Latinoamericano** - Arma el equipo titular con jugadores latinoamericanos

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

- **[Backend API](backend/README.md)** - FastAPI con 15 endpoints, 7 juegos
- **[Frontend](frontend/README.md)** - React + Vite, diseño FutFactos
- **[Scraping](scraping/README.md)** - Pipeline automatizado con 7 scrapers
- **[Deployment AWS](DEPLOYMENT.md)** - Guía completa de deployment (Quick Start + paso a paso) 🆕
- **[Infraestructura](terraform/README.md)** - Módulos de Terraform, variables, outputs 🆕

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

### 🔵⚪ Clásico del Día 🆕
Adivina la formación titular de un clásico histórico vs Newell's.
- **11 jugadores titulares + DT**
- **3 Modos de Dificultad:**
  - **🌴 Potrero:** 3 pistas + 3 revelaciones + sin límite
  - **🏆 Clásico:** 3 pistas + sin límite
  - **💪 Hazaña:** 3 pistas + 60 segundos ⏱️
- **Formaciones reales de Transfermarkt** (4-3-3, 4-2-3-1, 3-5-2, etc.)
- **Datos del partido:** Fecha, competición, resultado, árbitro
- **Sistema de pistas:** Primera letra del apellido + otro club donde jugó
- **Revelación de jugadores** con fotos y posiciones correctas
- **Validación del resultado** del partido
- ~63 clásicos históricos disponibles

### 🇦🇷 Equipo Nacional / 🌍 Europeo / 🌎 Latinoamericano
Arma el equipo titular adivinando jugadores por clubes.
- 11 jugadores + DT
- **3 Modos de Dificultad:**
  - **🌴 Potrero:** 3 pistas + 3 revelaciones de jugador + sin límite
  - **🏆 Clásico:** 3 pistas + sin límite de tiempo
  - **💪 Hazaña:** 3 pistas + 60 segundos ⏱️
- Formaciones dinámicas (4-3-3, 4-4-2, 3-5-2, 4-3-2-1)
- Sistema de pistas inteligentes (letra, posición, club)
- Selector de posición para jugadores polivalentes
- Revelación automática de jugadores (modo Potrero)

---

## 📊 Datos Disponibles

| Tipo | Cantidad | Ubicación |
|------|----------|-----------|
| Jugadores | ~1,600 | `scraping/data/output/rosario_central_jugadores.json` |
| Técnicos | ~65 | `scraping/data/output/rosario_central_tecnicos.json` |
| Relaciones | 65 técnicos | `scraping/data/output/rosario_central_tecnicos_jugadores.json` |
| Goles | Miles | `scraping/data/output/rosario_central_goles_detallados.json` |
| **Clásicos vs Newell's** 🆕 | ~63 partidos | `scraping/data/output/rosario_central_clasicos_game.json` |
| **Índice Optimizado** | 856 clubes | `scraping/data/output/club_posicion_index.json` |
| Logos Clubes | ~300 | `scraping/data/images/clubes/` |
| Fotos Jugadores | ~1,600 | `scraping/data/images/jugadores/` |
| Fotos Técnicos | ~65 | `scraping/data/images/tecnicos/` |
| Imágenes Personalizadas | 6 | `scraping/data/images/otras/` |

**Generar datos nuevos:** `cd scraping && python scripts/run_pipeline.py`

### 🚀 Optimizaciones
- **Índice club-posición:** Búsqueda O(1) vs O(N*M)
- **Imágenes optimizadas:** <400KB cada una
- **Lazy loading:** Imágenes cargadas bajo demanda

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
# Pipeline completo (recomendado)
cd scraping && python scripts/run_pipeline.py

# O individual
python scripts/run_jugadores.py  # Jugadores
python scripts/run_tecnicos.py   # Técnicos
python scripts/run_equipos.py    # Logos de clubes
```

---

## 🚢 Deploy

### ☁️ AWS (Recomendado - Ultra Low-Cost) 🆕

**Infraestructura completa con Terraform + CI/CD:**

```bash
# Ver guía completa
cat DEPLOYMENT.md  # Incluye Quick Start (5 pasos) + guía completa

# Setup inicial
cd terraform
terraform init
terraform plan
terraform apply

# O usar script helper
./deploy.sh
```

**Arquitectura:**
- **Frontend:** S3 + CloudFront (CDN global)
- **Backend:** EC2 t4g.micro (Free Tier)
- **CI/CD:** GitHub Actions (auto-deploy en push a `main`)
- **Costo estimado:** $0-3/mes (Free Tier elegible)

**Documentación completa:**
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Quick Start (5 pasos) + Arquitectura + CI/CD
- **[terraform/README.md](terraform/README.md)** - Módulos, variables, outputs

---

### 🔧 Alternativas

#### Backend
```bash
# Railway, Fly.io, o similar
cd backend
railway up  # o fly deploy
```

#### Frontend
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
| **Proyecto** | [README.md](README.md) | Este archivo - Overview general |
| **Backend** | [backend/README.md](backend/README.md) | API REST, 15 endpoints, 7 juegos, Docker |
| **Frontend** | [frontend/README.md](frontend/README.md) | React app, 7 juegos, componentes, estilos |
| **Scraping** | [scraping/README.md](scraping/README.md) | 7 scrapers, pipeline, datos, performance |
| **Deployment AWS** 🆕 | [DEPLOYMENT.md](DEPLOYMENT.md) | Quick Start + guía completa, CI/CD, costos |
| **Infraestructura** 🆕 | [terraform/README.md](terraform/README.md) | Módulos Terraform, variables, outputs |
| **Quickstart** | [QUICKSTART.md](QUICKSTART.md) | Inicio rápido para desarrollo local |

---

## 📊 Estadísticas

- **Líneas de código:** ~8,500+
- **Archivos creados:** ~60+
- **Juegos:** 7 (Nacional, Internacional, Órbita, Clásico, 3 Equipos)
- **Datos recopilados:** 
  - ~1,600 jugadores
  - 65 técnicos
  - 63 partidos clásicos históricos 🆕
  - 856 clubes indexados
- **Imágenes:** ~2,000 (jugadores, técnicos, clubes, personalizadas)
- **Performance:** 
  - Backend: <50ms por request
  - Frontend: 60fps constante
  - Imágenes: <400KB optimizadas
  - Transiciones: 150-200ms
- **Infraestructura:**
  - Terraform modules: 3 (networking, frontend, backend)
  - CI/CD: GitHub Actions
  - AWS Free Tier compatible

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

**Versión:** 3.0.0  
**Última actualización:** 2026-03-07  
**Diseño:** Inspirado en FutFactos.com  
**Idioma:** Español argentino (voseo)  
**Deployment:** AWS-ready con Terraform + CI/CD  
**Juegos:** 7 completos (incluyendo Clásico del Día)
