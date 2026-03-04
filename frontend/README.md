# 🎨 Frontend - FutFactos Rosario Central

Aplicación React con 6 juegos de trivia de fútbol, diseño inspirado en FutFactos.com.

> **[← Volver al README principal](../README.md)**

---

## 🎯 Características

- ✅ 6 juegos interactivos (Trayectoria + Órbita + Equipo)
- ✅ **3 Modos de dificultad** (Potrero, Clásico, Hazaña)
- ✅ **Sistema de pistas inteligentes** (letra, posición, club)
- ✅ **Revelación automática** de jugadores (modo Potrero)
- ✅ **Timer de 60s** (modo Hazaña)
- ✅ **Diseño FutFactos** (fondo azul oscuro #041742, amarillo #f3b229)
- ✅ **Responsive dinámico** con `clamp()` (mobile/tablet/desktop)
- ✅ **Imágenes personalizadas** (Rubén, Di María, Bauza)
- ✅ Sistema de formaciones dinámicas (4-3-3, 4-4-2, 3-5-2, 4-3-2-1)
- ✅ Selector de posición/jugador para múltiples opciones
- ✅ Sistema de vidas, timer y pistas
- ✅ **Animaciones optimizadas** (150-200ms, GPU-accelerated)
- ✅ **Textos argentinizados** (voseo)
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

### 4. 🇦🇷 Equipo Nacional
**Página:** `/equipo-nacional`

Arma el equipo titular con jugadores argentinos.
- **Selector de Dificultad:**
  - 🌴 **Potrero**: 3 pistas + 3 revelaciones
  - 🏆 **Clásico**: 3 pistas solamente
  - 💪 **Hazaña**: 3 pistas + timer 60s
- 11 jugadores + DT
- Formaciones dinámicas (4-3-3, 4-4-2, 3-5-2, 4-3-2-1)
- Pistas inteligentes (letra, posición, otro club)
- Selector de posición/jugador
- Layout 2 columnas (club+controles | campo táctico)

### 5. 🌍 Equipo Europeo
**Página:** `/equipo-europeo`

Arma el equipo titular con jugadores europeos.
- Mismas dificultades y mecánicas que Equipo Nacional
- Clubes europeos (Juventus, Bayern, etc.)
- Imágenes personalizadas (Di María)

### 6. 🌎 Equipo Latinoamericano
**Página:** `/equipo-latinoamericano`

Arma el equipo titular con jugadores latinoamericanos.
- Mismas dificultades y mecánicas que Equipo Nacional
- Clubes latinoamericanos (Boca, River, Flamengo, etc.)
- Imágenes personalizadas (Bauza)

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
│   │   ├── EquipoEuropeo.jsx       # Wrapper
│   │   └── EquipoLatinoamericano.jsx  # Wrapper
│   ├── components/         # Componentes reutilizables
│   │   ├── EquipoGame.jsx  # Lógica genérica de juegos de equipo
│   │   └── DifficultySelector.jsx  # Selector de dificultad (NUEVO)
│   ├── services/
│   │   └── api.js          # Axios client
│   ├── styles/             # CSS por página
│   │   ├── variables.css   # Sistema de diseño FutFactos
│   │   ├── index.css       # Globales
│   │   ├── App.css         # Navbar + layout (diseño FutFactos)
│   │   ├── HomePage.css    # Tarjetas de juegos (diseño FutFactos)
│   │   ├── TrayectoriaGame.css
│   │   ├── OrbitaGame.css
│   │   ├── EquipoGame.css  # Juegos de equipo
│   │   └── DifficultySelector.css  # Selector de dificultad (NUEVO)
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

### Imágenes Personalizadas

Cada tipo de juego tiene su propia imagen:

| Juego | Imagen | Optimización |
|-------|--------|--------------|
| 🇦🇷 Equipo Nacional | `ruben.jpg` (Marco Rubén) | 84KB |
| 🌍 Equipo Europeo | `di_maria.jpg` (Di María) | 60KB (88% reducción) |
| 🌎 Equipo Latinoamericano | `bauza.webp` (Bauza) | 27KB |
| 🌴 Potrero | `palma.webp` | 32KB |
| 🏆 Clásico | `miguel.png` | 339KB (88% reducción) |
| 💪 Hazaña | `petaco.avif` | 118KB |

**Técnica:** `object-position` ajustado para mejor encuadre (ej: `center 70%` para Rubén).

---

## 🔌 API Client

**Archivo:** `src/services/api.js`

```javascript
import { gamesAPI } from './services/api'

// Obtener juego
const game = await gamesAPI.getEquipoNacional()

// Verificar respuesta
const result = await gamesAPI.verifyGuess(
  gameId, 
  'equipo_nacional', 
  'Marco Ruben'
)
console.log(result.correcto) // true/false

// Confirmar posición (jugador polivalente)
const result = await gamesAPI.confirmarPosicion(gameId, 'DEL')

// Confirmar jugador (múltiples coincidencias)
const result = await gamesAPI.confirmarJugador(gameId, 'marco_ruben')

// Obtener pista (NUEVO)
const pista = await gamesAPI.obtenerPista(gameId)
// { letra_apellido: "R", posicion_principal: "DEL", otro_club: "Dynamo Kyiv" }

// Revelar jugador aleatorio (NUEVO)
const result = await gamesAPI.revelarJugadorAleatorio(gameId)
// { jugador_revelado: {...}, posicion_asignada: "DEL", nuevo_club: {...} }
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

### EquipoGame (Componente Genérico)
```jsx
// Usado por: EquipoNacional, EquipoEuropeo, EquipoLatinoamericano
const [formacionData, setFormacionData] = useState({
  porteros: [], defensas: [], mediocampos: [], 
  mediocampistasOfensivos: [], delanteros: [], entrenador: null
})

// Dificultad (NUEVO)
const [difficulty, setDifficulty] = useState(null)
const [pistasRestantes, setPistasRestantes] = useState(3)
const [revelacionesRestantes, setRevelacionesRestantes] = useState(3)
const [timer, setTimer] = useState(60)
const [timerActive, setTimerActive] = useState(false)

// Selectores
const [mostrarSelectorPosicion, setMostrarSelectorPosicion] = useState(false)
const [mostrarSelectorJugador, setMostrarSelectorJugador] = useState(false)
const [posicionesDisponibles, setPosicionesDisponibles] = useState([])
const [jugadoresDisponibles, setJugadoresDisponibles] = useState([])

// Pista (NUEVO)
const [pista, setPista] = useState(null)
```

### DifficultySelector (NUEVO)
```jsx
// Modal para elegir dificultad antes de empezar
const difficulties = [
  { id: 'facil', name: 'POTRERO', icon: 'palma.webp', 
    features: ['3 pistas', '3 revelaciones', 'Sin límite'] },
  { id: 'intermedio', name: 'CLÁSICO', icon: 'miguel.png',
    features: ['3 pistas', 'Sin límite'] },
  { id: 'dificil', name: 'HAZAÑA', icon: 'petaco.avif',
    features: ['3 pistas', '60 segundos'] }
]
```

---

## 🎨 Estilos Destacados

### Animaciones Optimizadas

```css
/* Revelación de clubes */
.club-item.revealed {
  animation: revealPulse 0.6s ease;
}

/* Timer con alerta */
.timer.danger {
  animation: pulse 1s infinite;
}

/* Optimizaciones de Performance */
.game-card {
  transition: transform 0.2s ease, box-shadow 0.15s ease;  /* Específicas, no 'all' */
  will-change: transform;  /* GPU acceleration */
}

.game-card:hover {
  transform: scale(1.06);  /* Reducido desde 1.08 */
}
```

**Optimizaciones aplicadas:**
- ✅ `transition: all` → propiedades específicas
- ✅ Duraciones reducidas: 300ms → 150-200ms
- ✅ `will-change: transform` para GPU acceleration
- ✅ `transform: scale` reducido para menos jank
- ✅ Imágenes optimizadas (<400KB)
- ✅ `loading="eager"` + `decoding="async"` en imágenes críticas

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
**Idioma:** Español argentino (voseo)  
**Última actualización:** 2026-03-04  
**Performance:** 60fps con animaciones optimizadas
