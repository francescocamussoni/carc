# ⚡ Quick Start

Guía rápida para ejecutar FutFactos en 2 minutos.

---

## 🎯 Setup Automático (Recomendado)

```bash
# 1. Setup (solo primera vez)
./setup.sh

# 2. Ejecutar
./start.sh

# 3. Abrir navegador
# → http://localhost:3000
```

**¡Listo!** 🎉

---

## 📦 Setup Manual

### Si tienes `uv` (rápido ⚡)

```bash
# Backend
cd backend
uv venv && source .venv/bin/activate
uv pip install -r requirements.txt

# Frontend  
cd ../frontend
npm install
```

### Si no tienes `uv`

**Instalar uv primero:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**O usar pip tradicional:**
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## 🚀 Ejecutar

### Automático
```bash
./start.sh
```

### Manual

**Terminal 1 - Backend:**
```bash
cd backend
source .venv/bin/activate
python run.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

---

## 🌐 URLs

- **App:** http://localhost:3000
- **API Docs:** http://localhost:8000/docs
- **API:** http://localhost:8000

---

## 🎮 Probar

1. Abrir http://localhost:3000
2. Click en "Trayectoria Nacional" 🇦🇷
3. Adivinar jugador
4. ¡Jugar! ⚽

---

## 🐛 Problemas Comunes

### "command not found: uv"
```bash
# Instalar uv
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### "Port already in use"
```bash
# Matar procesos
lsof -ti :8000 | xargs kill -9  # Backend
lsof -ti :3000 | xargs kill -9  # Frontend
```

### "No module named 'fastapi'"
```bash
cd backend
source .venv/bin/activate  # Activar venv primero
uv pip install -r requirements.txt
```

---

## 📚 Más Info

- **[README completo](README.md)** - Documentación completa
- **[Backend](backend/README.md)** - API docs
- **[Frontend](frontend/README.md)** - React app

---

**Tiempo total: ~2 minutos** ⚡
