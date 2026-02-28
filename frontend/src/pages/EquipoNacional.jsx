import { useState, useEffect } from 'react'
import { gamesAPI, getImageUrl } from '../services/api'
import '../styles/EquipoGame.css'

function EquipoNacional() {
  const [gameData, setGameData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [guess, setGuess] = useState('')
  const [jugadoresRevelados, setJugadoresRevelados] = useState([])
  const [pistasUsadas, setPistasUsadas] = useState(0)
  const [mensaje, setMensaje] = useState('')
  const [gameOver, setGameOver] = useState(false)

  useEffect(() => {
    fetchGame()
  }, [])

  const fetchGame = async () => {
    try {
      setLoading(true)
      const data = await gamesAPI.getEquipoNacional()
      setGameData(data.data)
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
        'equipo_nacional',
        guess
      )

      if (result.correcto) {
        const jugadorRevelado = result.jugador_revelado
        setJugadoresRevelados([...jugadoresRevelados, jugadorRevelado.nombre])
        setMensaje(`✅ ¡Correcto! ${jugadorRevelado.nombre} - ${jugadorRevelado.posicion}`)
        
        // Check victory
        if (jugadoresRevelados.length + 1 >= 11) {
          setGameOver(true)
          setMensaje('🎉 ¡Felicitaciones! Completaste el equipo')
        }
      } else {
        setMensaje('❌ ' + result.mensaje)
      }

      setGuess('')

      setTimeout(() => setMensaje(''), 3000)
    } catch (err) {
      setMensaje('Error al verificar la respuesta')
    }
  }

  const usarPista = () => {
    if (pistasUsadas < gameData.pistas_disponibles && !gameOver) {
      const jugadoresNoRevelados = gameData.jugadores.filter(
        j => !jugadoresRevelados.includes(j.nombre_completo)
      )
      
      if (jugadoresNoRevelados.length > 0) {
        const random = Math.floor(Math.random() * jugadoresNoRevelados.length)
        const jugador = jugadoresNoRevelados[random]
        setMensaje(`💡 Pista: ${jugador.posicion} - ${jugador.nacionalidad || 'Argentino'}`)
        setPistasUsadas(pistasUsadas + 1)
        
        setTimeout(() => setMensaje(''), 5000)
      }
    }
  }

  const rendirse = () => {
    setGameOver(true)
    setJugadoresRevelados(gameData.jugadores.map(j => j.nombre_completo))
    setMensaje('Te rendiste. Aquí está el equipo completo.')
  }

  // Organizar jugadores por línea según formación 3-4-3
  const organizarFormacion = () => {
    if (!gameData) return { portero: [], defensores: [], mediocampistas: [], delanteros: [] }
    
    const portero = gameData.jugadores.filter(j => j.posicion === 'PO')
    const defensores = gameData.jugadores.filter(j => ['DC', 'ED', 'EI'].includes(j.posicion))
    const mediocampistas = gameData.jugadores.filter(j => ['MC', 'MD', 'MI'].includes(j.posicion))
    const delanteros = gameData.jugadores.filter(j => j.posicion === 'CT')

    return { portero, defensores, mediocampistas, delanteros }
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

  const formacion = organizarFormacion()
  const progreso = jugadoresRevelados.length
  const total = gameData?.jugadores.length || 11

  return (
    <div className="equipo-game">
      <div className="game-header">
        <h1>🇦🇷 Equipo Nacional del Día</h1>
        <p className="game-subtitle">
          {gameData?.dt_nombre && `DT: ${gameData.dt_nombre}`}
          {gameData?.competencia && ` - ${gameData.competencia}`}
        </p>
        <div className="game-stats">
          <div className="progreso-container">
            <span className="label">Progreso:</span>
            <span className="progreso">{progreso} / {total}</span>
          </div>
          <div className="pistas-container">
            <span className="label">Pistas:</span>
            <span className="pistas">{pistasUsadas} / {gameData?.pistas_disponibles || 3}</span>
          </div>
        </div>
      </div>

      {gameOver && (
        <div className="game-result victoria">
          <h2>🎉 Juego Terminado</h2>
          <p>Adivinaste {progreso} de {total} jugadores</p>
        </div>
      )}

      <div className="campo-futbol">
        <div className="esquema-titulo">ESQUEMA = {gameData?.formacion || '3-4-3'}</div>
        
        {/* Delanteros */}
        <div className="linea linea-delanteros">
          {formacion.delanteros.map((jugador, idx) => (
            <div key={idx} className="jugador-slot">
              <div className={`jugador-circle ${jugadoresRevelados.includes(jugador.nombre_completo) ? 'revelado' : 'oculto'}`}>
                {jugadoresRevelados.includes(jugador.nombre_completo) ? (
                  <img 
                    src={getImageUrl(jugador.image_url)} 
                    alt={jugador.apellido}
                    onError={(e) => e.target.style.display = 'none'}
                  />
                ) : (
                  <span className="jugador-silhouette">👤</span>
                )}
              </div>
              <div className="jugador-info">
                <span className="posicion">{jugador.posicion}</span>
                {jugadoresRevelados.includes(jugador.nombre_completo) && (
                  <span className="nombre">{jugador.apellido}</span>
                )}
              </div>
            </div>
          ))}
        </div>

        {/* Mediocampistas */}
        <div className="linea linea-mediocampistas">
          {formacion.mediocampistas.map((jugador, idx) => (
            <div key={idx} className="jugador-slot">
              <div className={`jugador-circle ${jugadoresRevelados.includes(jugador.nombre_completo) ? 'revelado' : 'oculto'}`}>
                {jugadoresRevelados.includes(jugador.nombre_completo) ? (
                  <img 
                    src={getImageUrl(jugador.image_url)} 
                    alt={jugador.apellido}
                    onError={(e) => e.target.style.display = 'none'}
                  />
                ) : (
                  <span className="jugador-silhouette">👤</span>
                )}
              </div>
              <div className="jugador-info">
                <span className="posicion">{jugador.posicion}</span>
                {jugadoresRevelados.includes(jugador.nombre_completo) && (
                  <span className="nombre">{jugador.apellido}</span>
                )}
              </div>
            </div>
          ))}
        </div>

        {/* Defensores */}
        <div className="linea linea-defensores">
          {formacion.defensores.map((jugador, idx) => (
            <div key={idx} className="jugador-slot">
              <div className={`jugador-circle ${jugadoresRevelados.includes(jugador.nombre_completo) ? 'revelado' : 'oculto'}`}>
                {jugadoresRevelados.includes(jugador.nombre_completo) ? (
                  <img 
                    src={getImageUrl(jugador.image_url)} 
                    alt={jugador.apellido}
                    onError={(e) => e.target.style.display = 'none'}
                  />
                ) : (
                  <span className="jugador-silhouette">👤</span>
                )}
              </div>
              <div className="jugador-info">
                <span className="posicion">{jugador.posicion}</span>
                {jugadoresRevelados.includes(jugador.nombre_completo) && (
                  <span className="nombre">{jugador.apellido}</span>
                )}
              </div>
            </div>
          ))}
        </div>

        {/* Portero */}
        <div className="linea linea-portero">
          {formacion.portero.map((jugador, idx) => (
            <div key={idx} className="jugador-slot">
              <div className={`jugador-circle ${jugadoresRevelados.includes(jugador.nombre_completo) ? 'revelado' : 'oculto'}`}>
                {jugadoresRevelados.includes(jugador.nombre_completo) ? (
                  <img 
                    src={getImageUrl(jugador.image_url)} 
                    alt={jugador.apellido}
                    onError={(e) => e.target.style.display = 'none'}
                  />
                ) : (
                  <span className="jugador-silhouette">👤</span>
                )}
              </div>
              <div className="jugador-info">
                <span className="posicion">{jugador.posicion}</span>
                {jugadoresRevelados.includes(jugador.nombre_completo) && (
                  <span className="nombre">{jugador.apellido}</span>
                )}
              </div>
            </div>
          ))}
        </div>

        {/* DT al costado */}
        {gameData?.dt_nombre && (
          <div className="dt-container">
            <div className="dt-circle">
              <span>🧑‍💼</span>
            </div>
            <span className="dt-label">DT</span>
          </div>
        )}
      </div>

      {!gameOver && (
        <div className="game-controls">
          <form onSubmit={handleSubmit} className="guess-form">
            <input
              type="text"
              value={guess}
              onChange={(e) => setGuess(e.target.value)}
              placeholder="Apellido del jugador..."
              className="guess-input"
              disabled={gameOver}
              autoFocus
            />
            <button type="submit" className="btn btn-primary" disabled={!guess.trim() || gameOver}>
              Enviar
            </button>
          </form>

          <div className="action-buttons">
            <button
              className="btn btn-secondary"
              onClick={usarPista}
              disabled={pistasUsadas >= (gameData?.pistas_disponibles || 3) || gameOver}
            >
              Mostrar Pista ({pistasUsadas}/{gameData?.pistas_disponibles || 3})
            </button>
            <button className="btn btn-danger" onClick={rendirse}>
              Rendirse
            </button>
          </div>
        </div>
      )}

      {mensaje && (
        <div className={`mensaje ${mensaje.includes('✅') ? 'success-message' : mensaje.includes('❌') ? 'error-message' : 'info-message'}`}>
          {mensaje}
        </div>
      )}
    </div>
  )
}

export default EquipoNacional
