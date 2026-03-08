# 🎨 Frontend - FutFactos Rosario Central

Aplicación React con 6 juegos de trivia de fútbol, diseño inspirado en FutFactos.com.

> **[← Volver al README principal](../README.md)**

---

## 🎯 Características

- ✅ **7 juegos interactivos** (Trayectoria + Órbita + Clásico + 3 Equipos) 🆕
- ✅ **3 Modos de dificultad** (Potrero, Clásico, Hazaña)
- ✅ **Sistema de pistas inteligentes** (letra, posición, club)
- ✅ **Revelación automática** de jugadores (modo Potrero)
- ✅ **Timer de 60s** (modo Hazaña)
- ✅ **Diseño FutFactos** (fondo azul oscuro #041742, amarillo #f3b229)
- ✅ **Responsive dinámico** con `clamp()` (mobile/tablet/desktop)
- ✅ **Imágenes personalizadas** (Rubén, Di María, Bauza)
- ✅ **Sistema de formaciones dinámicas** (4-3-3, 4-2-3-1, 3-5-2, 3-4-1-2, etc.) 🆕
- ✅ **Juego del Clásico** con formaciones reales vs Newell's 🆕
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

### 4. 🔵⚪ Clásico del Día (NUEVO) 🆕
**Página:** `/clasico-del-dia`

Adivina la formación titular de un clásico histórico vs Newell's.
- **Selector de Dificultad:**
  - 🌴 **Potrero**: 3 pistas + 3 revelaciones + sin límite
  - 🏆 **Clásico**: 3 pistas + sin límite
  - 💪 **Hazaña**: 3 pistas + timer 60s
- **11 jugadores titulares + DT**
- **Formaciones reales de Transfermarkt** (4-3-3, 4-2-3-1, 3-5-2, 3-4-1-2, etc.)
- **Layout mejorado:**
  - Panel superior: Progreso (jugadores, técnico), resultado, árbitro
  - Panel lateral: Info del clásico + controles
  - Panel central: Esquema táctico + entrenador
- **Pistas inteligentes:** Primera letra + otro club donde jugó
- **Revelar jugadores:** Muestra foto, nombre y posición
- **Validar resultado:** Adivina el marcador final
- ~63 clásicos históricos disponibles

### 5. 🇦🇷 Equipo Nacional
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

### 6. 🌍 Equipo Europeo
**Página:** `/equipo-europeo`

Arma el equipo titular con jugadores europeos.
- Mismas dificultades y mecánicas que Equipo Nacional
- Clubes europeos (Juventus, Bayern, etc.)
- Imágenes personalizadas (Di María)

### 7. 🌎 Equipo Latinoamericano
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
│   ├── pages/              # 8 páginas
│   │   ├── HomePage.jsx
│   │   ├── TrayectoriaNacional.jsx
│   │   ├── TrayectoriaInternacional.jsx
│   │   ├── OrbitaDelDia.jsx
│   │   ├── ClasicoDelDia.jsx       # Wrapper para Clásico (NUEVO) 🆕
│   │   ├── EquipoNacional.jsx      # Wrapper para Equipo Nacional
│   │   ├── EquipoEuropeo.jsx       # Wrapper para Equipo Europeo
│   │   └── EquipoLatinoamericano.jsx  # Wrapper para Equipo Latinoamericano
│   ├── components/         # Componentes reutilizables
│   │   ├── EquipoGame.jsx  # Lógica genérica de juegos de equipo/clásico
│   │   ├── ClasicoGame.jsx # Lógica específica del Clásico (NUEVO) 🆕
│   │   └── DifficultySelector.jsx  # Selector de dificultad
│   ├── services/
│   │   └── api.js          # Axios client (endpoints del clásico incluidos)
│   ├── styles/             # CSS por página
│   │   ├── variables.css   # Sistema de diseño FutFactos
│   │   ├── index.css       # Globales
│   │   ├── App.css         # Navbar + layout (diseño FutFactos)
│   │   ├── HomePage.css    # Tarjetas de juegos (diseño FutFactos)
│   │   ├── TrayectoriaGame.css
│   │   ├── OrbitaGame.css
│   │   ├── EquipoGame.css  # Juegos de equipo + clásico (compartido)
│   │   └── DifficultySelector.css  # Selector de dificultad
│   ├── App.jsx             # Router (incluye /clasico-del-dia)
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

// Obtener juegos
const game = await gamesAPI.getEquipoNacional()
const clasico = await gamesAPI.getClasicoDelDia()  // NUEVO 🆕

// Verificar respuesta
const result = await gamesAPI.verifyGuess(
  gameId, 
  'equipo_nacional', 
  'Marco Ruben'
)
console.log(result.correcto) // true/false

// Verificar jugador del clásico (NUEVO) 🆕
const result = await gamesAPI.verifyClasicoAnswer(gameId, 'Ruben')

// Verificar resultado del clásico (NUEVO) 🆕
const result = await gamesAPI.verifyClasicoResultado(gameId, '2-1')

// Confirmar posición (jugador polivalente)
const result = await gamesAPI.confirmarPosicion(gameId, 'DEL')

// Confirmar jugador (múltiples coincidencias)
const result = await gamesAPI.confirmarJugador(gameId, 'marco_ruben')

// Obtener pista
const pista = await gamesAPI.obtenerPista(gameId)
// { letra_apellido: "R", posicion_principal: "DEL", otro_club: "Dynamo Kyiv" }

// Obtener pista del clásico (NUEVO) 🆕
const pista = await gamesAPI.obtenerPistaClasicoJugador(gameId)
// { letra_apellido: "R", otro_club: "Boca Juniors" }

// Revelar jugador aleatorio
const result = await gamesAPI.revelarJugadorAleatorio(gameId)
// { jugador_revelado: {...}, posicion_asignada: "DEL", nuevo_club: {...} }

// Revelar jugador del clásico (NUEVO) 🆕
const result = await gamesAPI.revelarJugadorClasicoAleatorio(gameId)
// { jugador_revelado: {...}, posicion_asignada: "DEL" }
```

---

## 🏗️ Componentes Principales

### HomePage
Landing page con 7 tarjetas de juegos (diseño FutFactos).

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

### ClasicoGame (Componente Específico) 🆕
```jsx
// Usado por: ClasicoDelDia
const [gameData, setGameData] = useState(null)
const [difficulty, setDifficulty] = useState(null)

// Formación del clásico (11 jugadores + entrenador)
const [formacionData, setFormacionData] = useState({
  porteros: [], defensas: [], mediocampos: [], 
  mediocampistasOfensivos: [], delanteros: [], entrenador: null
})

// Estado del juego
const [jugadoresAdivinados, setJugadoresAdivinados] = useState(0)
const [tecnicoAdivinado, setTecnicoAdivinado] = useState(false)
const [resultadoVerificado, setResultadoVerificado] = useState(false)
const [gameOver, setGameOver] = useState(false)

// Controles
const [respuesta, setRespuesta] = useState('')
const [resultado, setResultado] = useState('')
const [pistasRestantes, setPistasRestantes] = useState(3)
const [revelacionesRestantes, setRevelacionesRestantes] = useState(3)
const [timer, setTimer] = useState(60)
const [timerActive, setTimerActive] = useState(false)

// Feedback
const [mensajeFeedback, setMensajeFeedback] = useState('')
const [pista, setPista] = useState(null)
```

### EquipoGame (Componente Genérico)
```jsx
// Usado por: EquipoNacional, EquipoEuropeo, EquipoLatinoamericano
const [formacionData, setFormacionData] = useState({
  porteros: [], defensas: [], mediocampos: [], 
  mediocampistasOfensivos: [], delanteros: [], entrenador: null
})

// Dificultad
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

// Pista
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
- **[Deployment AWS](../DEPLOYMENT.md)** - Infraestructura y CI/CD 🆕

---

**React:** 18.2  
**Vite:** 5.0  
**Node:** 18+  
**Diseño:** FutFactos-inspired  
**Idioma:** Español argentino (voseo)  
**Última actualización:** 2026-03-07  
**Juegos:** 7 completos (incluyendo Clásico del Día)  
**Performance:** 60fps con animaciones optimizadas
