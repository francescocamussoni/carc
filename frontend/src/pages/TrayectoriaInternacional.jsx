import { useState, useEffect } from 'react'
import { gamesAPI, getImageUrl } from '../services/api'
import '../styles/TrayectoriaGame.css'

function TrayectoriaInternacional() {
  const [gameData, setGameData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [guess, setGuess] = useState('')
  const [vidas, setVidas] = useState(5)
  const [pistasReveladas, setPistasReveladas] = useState([])
  const [clubesRevelados, setclubesRevelados] = useState([])
  const [gameOver, setGameOver] = useState(false)
  const [victoria, setVictoria] = useState(false)
  const [mensaje, setMensaje] = useState('')
  const [jugadorRevelado, setJugadorRevelado] = useState(null)

  useEffect(() => {
    fetchGame()
  }, [])

  const fetchGame = async () => {
    try {
      setLoading(true)
      const data = await gamesAPI.getTrayectoriaInternacional()
      setGameData(data.data)
      setVidas(data.data.max_vidas || 5)
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
        'trayectoria_internacional',
        guess
      )

      setMensaje(result.mensaje)

      if (result.correcto) {
        setVictoria(true)
        setGameOver(true)
        setJugadorRevelado(result.jugador_revelado)
      } else {
        const newVidas = vidas - 1
        setVidas(newVidas)

        if (result.pista_nueva && !pistasReveladas.includes(result.pista_nueva)) {
          setPistasReveladas([...pistasReveladas, result.pista_nueva])
        }

        if (clubesRevelados.length < gameData.clubes_internacionales.length) {
          setclubesRevelados([...clubesRevelados, clubesRevelados.length])
        }

        if (newVidas <= 0) {
          setGameOver(true)
          setJugadorRevelado(gameData.jugador_oculto)
        }
      }

      setGuess('')
    } catch (err) {
      setMensaje('Error al verificar la respuesta')
    }
  }

  const handleRendirse = () => {
    setGameOver(true)
    setJugadorRevelado(gameData.jugador_oculto)
    setMensaje(`El jugador era: ${gameData.jugador_oculto.nombre}`)
  }

  const revelarClub = () => {
    if (clubesRevelados.length < gameData.clubes_internacionales.length && vidas > 0) {
      setclubesRevelados([...clubesRevelados, clubesRevelados.length])
      const newVidas = Math.max(0, vidas - 1)
      setVidas(newVidas)
      if (newVidas <= 0) {
        setGameOver(true)
        setJugadorRevelado(gameData.jugador_oculto)
      }
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
    <div className="trayectoria-game rosario-central">
      <div className="game-header">
        <h1>🌎 Trayectoria Internacional del Día</h1>
        <p className="game-subtitle">Adivina el jugador por su trayectoria en clubes internacionales</p>
        <div className="game-stats">
          <div className="vidas-container">
            <span className="label">Vidas:</span>
            <span className="vidas">{'❤️'.repeat(vidas)}{'🖤'.repeat(5 - vidas)}</span>
          </div>
        </div>
      </div>

      {gameOver && (
        <div className={`game-result ${victoria ? 'victoria' : 'derrota'}`}>
          {victoria ? (
            <>
              <h2>🎉 ¡Felicitaciones!</h2>
              <p>Adivinaste correctamente: <strong>{jugadorRevelado?.nombre}</strong></p>
            </>
          ) : (
            <>
              <h2>😢 Fin del juego</h2>
              <p>El jugador era: <strong>{jugadorRevelado?.nombre}</strong></p>
            </>
          )}
          {jugadorRevelado?.image_url && (
            <img
              src={getImageUrl(jugadorRevelado.image_url)}
              alt={jugadorRevelado.nombre}
              className="jugador-image-revealed"
              onError={(e) => e.target.style.display = 'none'}
            />
          )}
          <div className="player-info">
            <p><strong>Posición:</strong> {jugadorRevelado?.posicion}</p>
            <p><strong>Nacionalidad:</strong> {jugadorRevelado?.nacionalidad}</p>
            <p><strong>Partidos:</strong> {jugadorRevelado?.partidos}</p>
          </div>
        </div>
      )}

      <div className="trayectoria-container">
        <h3>Trayectoria de Clubes Internacionales</h3>
        <div className="clubes-grid">
          {gameData?.clubes_internacionales.map((club, index) => (
            <div
              key={index}
              className={`club-item ${clubesRevelados.includes(index) || gameOver ? 'revealed' : 'hidden'}`}
            >
              {clubesRevelados.includes(index) || gameOver ? (
                <>
                  {club.logo_url && (
                    <img
                      src={getImageUrl(club.logo_url)}
                      alt={club.nombre}
                      className="club-logo"
                      onError={(e) => e.target.style.display = 'none'}
                    />
                  )}
                  <div className="club-info">
                    <p className="club-name">{club.nombre}</p>
                    <p className="club-periodo">{club.pais}</p>
                    <p className="club-periodo">{club.periodo}</p>
                  </div>
                </>
              ) : (
                <div className="club-hidden">
                  <span className="question-mark">?</span>
                  <p className="club-pais">{club.pais}</p>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {pistasReveladas.length > 0 && (
        <div className="pistas-container">
          <h3>Pistas</h3>
          <ul className="pistas-list">
            {pistasReveladas.map((pista, index) => (
              <li key={index} className="pista-item">{pista}</li>
            ))}
          </ul>
        </div>
      )}

      {!gameOver && (
        <div className="game-controls">
          <form onSubmit={handleSubmit} className="guess-form">
            <input
              type="text"
              value={guess}
              onChange={(e) => setGuess(e.target.value)}
              placeholder="Ingresa el nombre del jugador..."
              className="guess-input"
              disabled={gameOver}
            />
            <button type="submit" className="btn btn-primary" disabled={!guess.trim() || gameOver}>
              Verificar
            </button>
          </form>

          <div className="action-buttons">
            <button
              className="btn btn-secondary"
              onClick={revelarClub}
              disabled={clubesRevelados.length >= gameData.clubes_internacionales.length || vidas <= 0}
            >
              Revelar Club (-1 vida)
            </button>
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

export default TrayectoriaInternacional
