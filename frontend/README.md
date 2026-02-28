# 🎨 Frontend - FutFactos Rosario Central

Aplicación React con 3 juegos de trivia de fútbol.

> **[← Volver al README principal](../README.md)**

---

## 🎯 Características

- ✅ 3 juegos interactivos
- ✅ Diseño responsive (mobile/tablet/desktop)
- ✅ Tema personalizado Rosario Central 🔵⚪
- ✅ Animaciones suaves
- ✅ Sistema de vidas y timer
- ✅ Feedback visual en tiempo real

---

## 🛠️ Instalación

```bash
cd frontend
npm install
```

---

## 🚀 Ejecutar

```bash
npm run dev
```

**URL:** http://localhost:3000

---

## 🎮 Juegos Implementados

### 1. 🇦🇷 Trayectoria Nacional
**Página:** `/trayectoria-nacional`

Adivina el jugador por clubes argentinos.
- 5 vidas ❤️
- Clubes se revelan progresivamente
- Botón "Revelar Club" (-1 vida)
- Pistas con errores

### 2. 🌎 Trayectoria Internacional
**Página:** `/trayectoria-internacional`

Adivina el jugador por clubes internacionales.
- Misma mecánica que Nacional
- Logos de clubes extranjeros

### 3. ⚽ Órbita del Día
**Página:** `/orbita`

Identifica jugadores dirigidos por un técnico.
- Timer de 120 segundos ⏱️
- Múltiples jugadores
- Progreso: X/Y adivinados
- 3 modos: más minutos/goles/apariciones

---

## 📂 Estructura

```
frontend/
├── src/
│   ├── pages/              # 4 páginas
│   │   ├── HomePage.jsx
│   │   ├── TrayectoriaNacional.jsx
│   │   ├── TrayectoriaInternacional.jsx
│   │   └── OrbitaDelDia.jsx
│   ├── services/
│   │   └── api.js          # Axios client
│   ├── styles/             # CSS por página
│   │   ├── index.css       # Globales + variables
│   │   ├── App.css         # Navbar + layout
│   │   ├── HomePage.css
│   │   ├── TrayectoriaGame.css
│   │   └── OrbitaGame.css
│   ├── App.jsx             # Router
│   └── main.jsx            # Entry point
├── package.json
└── vite.config.js
```

---

## 🎨 Diseño

### Colores (Rosario Central)

```css
--rc-blue: #003f7f       /* Azul principal */
--rc-yellow: #FFD100     /* Amarillo */
--rc-dark: #001f3f       /* Azul oscuro */
--rc-light-blue: #4a90e2 /* Celeste */
```

### Responsive

- **Desktop:** > 768px - Layout completo
- **Tablet:** 481-768px - Layout adaptado
- **Mobile:** < 480px - Layout vertical

---

## 🔌 API Client

**Archivo:** `src/services/api.js`

```javascript
import { gamesAPI } from './services/api'

// Obtener juego
const game = await gamesAPI.getTrayectoriaNacional()

// Verificar respuesta
const result = await gamesAPI.verifyGuess(
  gameId, 
  'trayectoria_nacional', 
  'Marco Ruben'
)

console.log(result.correcto) // true/false
```

---

## 🏗️ Componentes Principales

### HomePage
Landing page con 3 tarjetas de juegos.

### TrayectoriaNacional
```jsx
// Estados principales
const [gameData, setGameData] = useState(null)
const [vidas, setVidas] = useState(5)
const [clubesRevelados, setclubesRevelados] = useState([])
const [gameOver, setGameOver] = useState(false)
```

### OrbitaDelDia
```jsx
// Estados principales
const [tiempoRestante, setTiempoRestante] = useState(120)
const [elementosRevelados, setElementosRevelados] = useState([])
const [victoria, setVictoria] = useState(false)
```

---

## 🎨 Estilos Destacados

### Animaciones

```css
/* Revelación de clubes */
.club-item.revealed {
  animation: revealPulse 0.6s ease;
}

/* Timer con alerta */
.timer.danger {
  animation: pulse 1s infinite;
}
```

### Feedback Visual

```javascript
// Success
<div className="success-message">✅ ¡Correcto!</div>

// Error  
<div className="error-message">❌ Incorrecto</div>

// Loading
<div className="loading"><div className="spinner"></div></div>
```

---

## 🚀 Build para Producción

```bash
npm run build
```

Output: `dist/` (servir con nginx/apache/cdn)

---

## 🚢 Deploy

### Vercel (recomendado)

```bash
npm install -g vercel
vercel
```

### Netlify

```bash
npm run build
netlify deploy --prod --dir=dist
```

---

## 🔧 Configuración

### Variables de entorno

Crear `.env`:

```bash
VITE_API_URL=http://localhost:8000/api/v1
```

### Proxy (desarrollo)

**Archivo:** `vite.config.js`

```javascript
server: {
  port: 3000,
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true
    }
  }
}
```

---

## 🐛 Troubleshooting

### Imágenes no cargan
**Causa:** Backend no sirve static files.  
**Solución:** Verificar backend está corriendo y serving `../scraping/data/images/`

### CORS error
**Causa:** Backend no tiene `http://localhost:3000` en CORS origins.  
**Solución:** Verificar `backend/app/core/config.py`

### Build error
```bash
rm -rf node_modules package-lock.json
npm install
npm run build
```

---

## 🔗 Enlaces

- **[README Principal](../README.md)** - Overview del proyecto
- **[Backend API](../backend/README.md)** - API que consume
- **[Scraping](../scraping/README.md)** - Datos que muestra

---

**React:** 18.2  
**Vite:** 5.0  
**Node:** 18+
