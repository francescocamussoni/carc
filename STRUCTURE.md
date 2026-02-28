# 📁 Estructura del Proyecto

> **Nueva estructura limpia y organizada** ✨

```
carc/
│
├── 📦 backend/                    # API REST - FastAPI
│   ├── app/
│   │   ├── api/v1/endpoints/     # Endpoints de juegos
│   │   ├── core/                 # Config (paths a scraping/data/)
│   │   ├── schemas/              # Pydantic models
│   │   ├── services/             # Lógica de juegos
│   │   └── main.py               # FastAPI app
│   ├── requirements.txt
│   ├── run.py                    # Ejecutar servidor
│   └── README.md                 # 📖 Doc backend
│
├── 🎨 frontend/                   # App React - Vite
│   ├── src/
│   │   ├── pages/                # 4 páginas (Home + 3 juegos)
│   │   ├── services/api.js       # Cliente Axios
│   │   ├── styles/               # CSS por página
│   │   └── App.jsx               # React Router
│   ├── package.json
│   ├── vite.config.js
│   └── README.md                 # 📖 Doc frontend
│
├── 🔧 scraping/                   # Scrapers - Transfermarkt
│   ├── data/                     # ⭐ Datos generados
│   │   ├── output/               # 4 JSON files
│   │   │   ├── rosario_central_jugadores.json
│   │   │   ├── rosario_central_tecnicos.json
│   │   │   ├── rosario_central_tecnicos_jugadores.json
│   │   │   └── rosario_central_goles_detallados.json
│   │   └── images/               # 1,184 imágenes
│   │       ├── jugadores/        # 451 fotos
│   │       ├── tecnicos/         # 43 fotos
│   │       └── clubes/           # 690 logos
│   ├── scripts/                  # Ejecutables
│   │   ├── run_scraper.py        # Jugadores
│   │   ├── run_tecnicos.py       # Técnicos
│   │   ├── run_tecnicos_jugadores.py  # Relaciones
│   │   └── run_goles_detallados.py    # Goles
│   ├── src/                      # Código scraping
│   │   ├── scrapers/
│   │   ├── services/
│   │   ├── models/
│   │   └── config/
│   ├── requirements.txt
│   └── README.md                 # 📖 Doc scraping (4 scrapers)
│
├── 📚 README.md                   # 📖 Doc principal con hipervínculos
├── ⚡ QUICKSTART.md               # Guía rápida 2 min
├── 📋 STRUCTURE.md                # Este archivo (estructura)
├── 🔧 setup.sh                    # Setup automático (con uv)
├── 🚀 start.sh                    # Iniciar backend + frontend
└── 🙈 .gitignore
```

---

## 🎯 Ventajas de esta Estructura

### ✅ Separación Clara
Cada módulo es independiente:
- `backend/` - Solo backend
- `frontend/` - Solo frontend  
- `scraping/` - Solo scraping + data

### ✅ Sin Duplicados
- ❌ Ya no hay `src/` en raíz
- ❌ Ya no hay `scripts/` en raíz
- ❌ Ya no hay `data/` huérfano
- ✅ Todo en su lugar

### ✅ Data Centralizada
`scraping/data/` contiene:
- JSONs generados
- Imágenes descargadas
- Backend lee desde `../scraping/data/`

### ✅ Documentación Jerárquica
```
README.md (principal)
    ├─→ backend/README.md
    ├─→ frontend/README.md
    └─→ scraping/README.md (todo consolidado)
```

---

## 📖 Navegación de Docs

### Desde la raíz
- **[README.md](README.md)** - Inicio aquí
  - Ver [Backend](backend/README.md)
  - Ver [Frontend](frontend/README.md)
  - Ver [Scraping](scraping/README.md)

### Desde cada módulo
Cada README tiene link de vuelta:
```markdown
> **[← Volver al README principal](../README.md)**
```

---

## 🔄 Flujo de Datos

```
1. scraping/scripts/run_scraper.py
   ↓ genera
2. scraping/data/output/*.json
   ↓ lee
3. backend/app/services/data_loader.py
   ↓ sirve
4. frontend/src/services/api.js
   ↓ renderiza
5. frontend/src/pages/*.jsx
```

---

## 🚀 Comandos Útiles

### Ejecutar todo

```bash
./start.sh
```

### Por módulo

```bash
# Backend
cd backend && python run.py

# Frontend
cd frontend && npm run dev

# Scraping
cd scraping && python scripts/run_scraper.py
```

---

## 📦 Deploy

Cada módulo se puede deployar independientemente:

- **backend/** → Railway, Fly.io
- **frontend/** → Vercel, Netlify
- **scraping/** → Cron job en servidor

---

## ✨ Conclusión

**Estructura limpia, organizada y fácil de mantener.**

Cada módulo:
- ✅ Tiene su propio README
- ✅ Está autocontenido
- ✅ Se puede deployar independiente
- ✅ Tiene hipervínculos a otros módulos

---

**Versión:** 2.0  
**Reorganización:** 2026-02-28
