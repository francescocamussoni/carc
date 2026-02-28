#!/bin/bash

# Setup script para FutFactos Rosario Central
# Usa uv (rápido) si está disponible, sino pip

set -e

echo "🚀 Setup de FutFactos Rosario Central"
echo ""

# Check if uv is installed
if command -v uv &> /dev/null; then
    echo "✅ uv detectado - usando instalación rápida"
    USE_UV=true
else
    echo "⚠️  uv no encontrado - usando pip (más lento)"
    echo "   Instalar uv: curl -LsSf https://astral.sh/uv/install.sh | sh"
    USE_UV=false
fi

echo ""

# Backend setup
echo "📦 [1/2] Configurando Backend..."
cd backend

if [ "$USE_UV" = true ]; then
    uv venv .venv
    source .venv/bin/activate
    uv pip install -r requirements.txt
else
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
fi

echo "✅ Backend instalado"
cd ..

echo ""

# Frontend setup
echo "🎨 [2/2] Configurando Frontend..."
cd frontend

if command -v npm &> /dev/null; then
    npm install
    echo "✅ Frontend instalado"
else
    echo "❌ npm no encontrado. Instala Node.js primero."
    exit 1
fi

cd ..

echo ""
echo "🎉 ¡Setup completado!"
echo ""
echo "Para ejecutar:"
echo "  ./start.sh"
echo ""
echo "O manualmente:"
echo "  Terminal 1: cd backend && source .venv/bin/activate && python run.py"
echo "  Terminal 2: cd frontend && npm run dev"
echo ""
