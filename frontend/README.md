# 🎨 Frontend - FutFactos Rosario Central

Aplicación React con 6 juegos de trivia de fútbol, diseño inspirado en FutFactos.com.

> **[← Volver al README principal](../README.md)**

---

## 🎯 Características

- ✅ 6 juegos interactivos (Trayectoria + Órbita + Equipo)
- ✅ **Diseño FutFactos** (fondo azul oscuro, acentos amarillos)
- ✅ **Responsive dinámico** con `clamp()` (mobile/tablet/desktop)
- ✅ Sistema de formaciones dinámicas (4-3-3, 4-4-2, 3-5-2, 4-3-2-1)
- ✅ Selector de posición para jugadores polivalentes
- ✅ Sistema de vidas, timer y pistas
- ✅ Animaciones suaves
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

### 4. 🇦🇷 Equipo Nacional (NUEVO)
**Página:** `/equipo-nacional`

Arma el equipo titular con jugadores argentinos.
- 11 jugadores + DT
- Formaciones dinámicas
- Sistema de pistas
- Selector de posición

### 5. 🌍 Equipo Europeo (NUEVO)
**Página:** `/equipo-europeo`

Arma el equipo titular con jugadores europeos.
- Misma mecánica que Equipo Nacional
- Clubes europeos

### 6. 🌎 Equipo Latinoamericano (NUEVO)
**Página:** `/equipo-latinoamericano`

Arma el equipo titular con jugadores latinoamericanos.
- Misma mecánica que Equipo Nacional
- Clubes latinoamericanos

---

## 📂 Estructura

```
frontend/
├── src/
│   ├── pages/              # 7 páginas
│   │   ├── HomePage.jsx
│   │   ├── TrayectoriaNacional.jsx
│   │   ├── TrayectoriaInternacional.jsx
│   │   ├── OrbitaDelDia.jsx
│   │   ├── EquipoNacional.jsx      # Wrapper (NUEVO)
│   │   ├── EquipoEuropeo.jsx       # Wrapper (NUEVO)
│   │   └── EquipoLatinoamericano.jsx  # Wrapper (NUEVO)
│   ├── components/         # Componentes reutilizables (NUEVO)
│   │   └── EquipoGame.jsx  # Lógica genérica de juegos de equipo
│   ├── services/
│   │   └── api.js          # Axios client
│   ├── styles/             # CSS por página
│   │   ├── variables.css   # Sistema de diseño FutFactos (NUEVO)
│   │   ├── index.css       # Globales
│   │   ├── App.css         # Navbar + layout (diseño FutFactos)
│   │   ├── HomePage.css    # Tarjetas de juegos (diseño FutFactos)
│   │   ├── TrayectoriaGame.css
│   │   ├── OrbitaGame.css
│   │   └── EquipoGame.css  # Juegos de equipo (NUEVO)
│   ├── App.jsx             # Router
│   └── main.jsx            # Entry point
├── package.json
└── vite.config.js
```

---

## 🎨 Diseño FutFactos

### Colores

```css
/* Paleta FutFactos (variables.css) */
--primary-bg: #041742           /* Fondo azul oscuro */
--secondary-bg: #0a2454         /* Azul oscuro secundario */
--accent-yellow: #f3b229        /* Amarillo acentos */
--text-white: #ffffff           /* Texto blanco */
--text-gray: #a0a0a0            /* Texto secundario */
--border-gray: #2a3a5a          /* Bordes grises */
```

### Responsive Dinámico

Usa `clamp()` para escalado fluido:

```css
/* Ejemplo: Logo que escala entre 90px y 150px */
.club-logo {
  width: clamp(90px, 10vw, 150px);
  height: clamp(90px, 10vw, 150px);
}
```

- **Desktop:** > 768px - Layout completo, 2 columnas (juegos de equipo)
- **Tablet:** 481-768px - Layout adaptado
- **Mobile:** < 480px - Layout vertical, elementos más compactos

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
Landing page con 6 tarjetas de juegos (diseño FutFactos).

### TrayectoriaNacional / TrayectoriaInternacional
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

### EquipoGame (NUEVO - Componente Genérico)
```jsx
// Usado por: EquipoNacional, EquipoEuropeo, EquipoLatinoamericano
const [formacionData, setFormacionData] = useState({
  porteros: [], defensas: [], mediocampos: [], 
  mediocampistasOfensivos: [], delanteros: [], entrenador: null
})
const [mostrarSelectorPosicion, setMostrarSelectorPosicion] = useState(false)
const [posicionesDisponibles, setPosicionesDisponibles] = useState([])
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
**Diseño:** FutFactos-inspired  
**Última actualización:** 2026-03-03
