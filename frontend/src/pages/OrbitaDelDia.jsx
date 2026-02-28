import { useState, useEffect } from 'react'
import { gamesAPI, getImageUrl } from '../services/api'
import '../styles/OrbitaGame.css'

function OrbitaDelDia() {
  const [gameData, setGameData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [guess, setGuess] = useState('')
  const [tiempoRestante, setTiempoRestante] = useState(120)
  const [elementosRevelados, setElementosRevelados] = useState([])
  const [gameOver, setGameOver] = useState(false)
  const [victoria, setVictoria] = useState(false)
  const [mensaje, setMensaje] = useState('')

  useEffect(() => {
    fetchGame()
  }, [])

  useEffect(() => {
    if (!gameOver && tiempoRestante > 0) {
      const timer = setInterval(() => {
        setTiempoRestante((prev) => {
          if (prev <= 1) {
            setGameOver(true)
            setMensaje('¡Se acabó el tiempo!')
            return 0
          }
          return prev - 1
        })
      }, 1000)

      return () => clearInterval(timer)
    }
  }, [gameOver, tiempoRestante])

  useEffect(() => {
    // Check if all elements are revealed (victory condition)
    if (
      gameData &&
      elementosRevelados.length > 0 &&
      elementosRevelados.length === gameData.elementos_orbitales.length
    ) {
      setVictoria(true)
      setGameOver(true)
      setMensaje('¡Felicitaciones! Adivinaste todos los jugadores')
    }
  }, [elementosRevelados, gameData])

  const fetchGame = async () => {
    try {
      setLoading(true)
      const data = await gamesAPI.getOrbita()
      setGameData(data.data)
      setTiempoRestante(data.data.tiempo_limite || 120)
      setLoading(false)
    } catch (err) {
      setError('Error al cargar el juego. Intenta más tarde.')
      setLoading(false)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!guess.trim() || gameOver) return

    try {
      const result = await gamesAPI.verifyGuess(
        gameData.game_id,
        'orbita',
        guess,
        120 - tiempoRestante
      )

      if (result.correcto && result.elementos_revelados) {
        // Add new revealed elements
        const nuevosRevelados = result.elementos_revelados.filter(
          (nombre) => !elementosRevelados.includes(nombre)
        )
        setElementosRevelados([...elementosRevelados, ...nuevosRevelados])
        setMensaje(`✅ ¡Correcto! ${result.mensaje}`)
      } else {
        setMensaje(`❌ ${result.mensaje}`)
      }

      setGuess('')

      // Auto-clear message after 3 seconds
      setTimeout(() => {
        setMensaje('')
      }, 3000)
    } catch (err) {
      setMensaje('Error al verificar la respuesta')
    }
  }

  const handleRendirse = () => {
    setGameOver(true)
    // Reveal all elements
    if (gameData) {
      const allNames = gameData.elementos_orbitales.map((el) => el.nombre)
      setElementosRevelados(allNames)
    }
    setMensaje('Te rendiste. Aquí están todos los jugadores.')
  }

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  const getModoTexto = (modo) => {
    switch (modo) {
      case 'mas_minutos':
        return 'más minutos jugados'
      case 'mas_goles':
        return 'más goles'
      case 'mas_apariciones':
        return 'más apariciones'
      default:
        return modo
    }
  }

  if (loading) {
    return (
      <div className="loading">
        <div className="spinner"></div>
        <p>Cargando juego...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="error-message">
        <h2>Error</h2>
        <p>{error}</p>
        <button className="btn btn-primary" onClick={fetchGame}>
          Reintentar
        </button>
      </div>
    )
  }

  return (
    <div className="orbita-game rosario-central">
      <div className="game-header">
        <h1>⚽ Órbita del Día</h1>
        <p className="game-subtitle">
          Jugadores con {getModoTexto(gameData?.modo_juego)} en{' '}
          <strong>{gameData?.competencia}</strong>
        </p>
        <div className="game-stats">
          <div className="timer-container">
            <span className="label">⏱️ Tiempo:</span>
            <span className={`timer ${tiempoRestante < 30 ? 'danger' : ''}`}>
              {formatTime(tiempoRestante)}
            </span>
          </div>
          <div className="progress-container">
            <span className="label">Progreso:</span>
            <span className="progress">
              {elementosRevelados.length} / {gameData?.elementos_orbitales.length || 0}
            </span>
          </div>
        </div>
      </div>

      {gameOver && (
        <div className={`game-result ${victoria ? 'victoria' : 'derrota'}`}>
          {victoria ? (
            <>
              <h2>🎉 ¡Perfecto!</h2>
              <p>Adivinaste todos los jugadores en {formatTime(120 - tiempoRestante)}</p>
            </>
          ) : (
            <>
              <h2>⏰ Fin del juego</h2>
              <p>Adivinaste {elementosRevelados.length} de {gameData?.elementos_orbitales.length} jugadores</p>
            </>
          )}
        </div>
      )}

      <div className="orbita-container">
        {/* Protagonista (Técnico) en el centro */}
        <div className="protagonista-container">
          {gameData?.protagonista.image_url && (
            <img
              src={getImageUrl(gameData.protagonista.image_url)}
              alt={gameData.protagonista.nombre}
              className="protagonista-image"
              onError={(e) => e.target.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="100" height="100"%3E%3Crect fill="%23ddd" width="100" height="100"/%3E%3Ctext x="50%25" y="50%25" text-anchor="middle" dy=".3em" fill="%23999" font-size="14"%3E?%3C/text%3E%3C/svg%3E'}
            />
          )}
          <p className="protagonista-name">{gameData?.protagonista.nombre}</p>
          <p className="protagonista-role">Director Técnico</p>
        </div>

        {/* Elementos Orbitales (Jugadores) */}
        <div className="elementos-grid">
          {gameData?.elementos_orbitales.map((elemento, index) => {
            const isRevealed = elementosRevelados.includes(elemento.nombre) || gameOver
            return (
              <div
                key={elemento.id}
                className={`elemento-orbital ${isRevealed ? 'revealed' : 'hidden'}`}
                style={{ animationDelay: `${index * 0.1}s` }}
              >
                {isRevealed ? (
                  <>
                    {elemento.image_url && (
                      <img
                        src={getImageUrl(elemento.image_url)}
                        alt={elemento.nombre}
                        className="elemento-image"
                        onError={(e) => e.target.style.display = 'none'}
                      />
                    )}
                    <p className="elemento-name">{elemento.nombre}</p>
                  </>
                ) : (
                  <>
                    <div className="elemento-placeholder">
                      <span className="question-mark">?</span>
                    </div>
                    <p className="elemento-name-hidden">???</p>
                  </>
                )}
              </div>
            )
          })}
        </div>
      </div>

      {!gameOver && (
        <div className="game-controls">
          <form onSubmit={handleSubmit} className="guess-form">
            <input
              type="text"
              value={guess}
              onChange={(e) => setGuess(e.target.value)}
              placeholder="Ingresa el nombre de un jugador..."
              className="guess-input"
              disabled={gameOver}
              autoFocus
            />
            <button type="submit" className="btn btn-primary" disabled={!guess.trim() || gameOver}>
              Verificar
            </button>
          </form>

          <div className="action-buttons">
            <button className="btn btn-danger" onClick={handleRendirse}>
              Rendirse
            </button>
          </div>
        </div>
      )}

      {mensaje && (
        <div className={`mensaje ${victoria ? 'success-message' : gameOver ? 'error-message' : 'info-message'}`}>
          {mensaje}
        </div>
      )}
    </div>
  )
}

export default OrbitaDelDia
