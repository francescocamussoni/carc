import { useState, useEffect } from 'react'
import { gamesAPI } from '../services/api'
import '../styles/EquipoGame.css'

function EquipoNacional() {
  const [gameData, setGameData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [guess, setGuess] = useState('')
  const [clubActual, setClubActual] = useState(null)
  const [posiciones, setPosiciones] = useState([])
  const [entrenadorRevelado, setEntrenadorRevelado] = useState(false)
  const [mensaje, setMensaje] = useState('')
  const [gameOver, setGameOver] = useState(false)

  useEffect(() => {
    fetchGame()
  }, [])

  const fetchGame = async () => {
    try {
      setLoading(true)
      const data = await gamesAPI.getEquipoEuropeo()
      console.log('Game data:', data.data)
      setGameData(data.data)
      setPosiciones(data.data.posiciones || [])
      setClubActual(data.data.club_actual)
      setLoading(false)
    } catch (err) {
      console.error('Error loading game:', err)
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
        'equipo_europeo',
        guess
      )

      if (result.correcto) {
        setMensaje(`✅ ${result.mensaje}`)
        
        // Update positions from result
        if (result.posicion_asignada) {
          const newPosiciones = [...posiciones]
          // Find first empty position matching the assigned one
          const idx = newPosiciones.findIndex(
            p => p.posicion === result.posicion_asignada && !p.revelado
          )
          if (idx !== -1) {
            newPosiciones[idx] = {
              ...newPosiciones[idx],
              revelado: true,
              jugador_nombre: result.jugador_revelado.nombre,
              jugador_apellido: result.jugador_revelado.apellido || result.jugador_revelado.nombre.split(' ').pop(),
              image_url: result.jugador_revelado.image_url
            }
            setPosiciones(newPosiciones)
          }
        }

        // Update club if there's a new one
        if (result.nuevo_club) {
          setClubActual(result.nuevo_club)
        }

        // Check if it was the coach
        if (result.jugador_revelado?.tipo === 'entrenador') {
          setEntrenadorRevelado(true)
        }

        // Check victory
        const revelados = posiciones.filter(p => p.revelado).length
        if (revelados >= 10 && entrenadorRevelado) {
          setGameOver(true)
          setMensaje('🎉 ¡Felicitaciones! Completaste el equipo')
        }
      } else {
        setMensaje('❌ ' + result.mensaje)
      }

      setGuess('')
      setTimeout(() => {
        if (!result.correcto) setMensaje('')
      }, 3000)
    } catch (err) {
      console.error('Error verifying guess:', err)
      setMensaje('Error al verificar la respuesta')
      setTimeout(() => setMensaje(''), 3000)
    }
  }

  const organizarFormacion = () => {
    if (!posiciones || posiciones.length === 0) {
      return { portero: [], defensores: [], mediocampistas: [], delanteros: [] }
    }
    
    const portero = posiciones.filter(p => p.posicion === 'PO')
    const defensores = posiciones.filter(p => ['DC', 'ED', 'EI'].includes(p.posicion))
    const mediocampistas = posiciones.filter(p => ['MC', 'MD', 'MI'].includes(p.posicion))
    const delanteros = posiciones.filter(p => p.posicion === 'DC' && defensores.every(d => d !== p))

    return {
      portero,
      defensores: {
        central: defensores.filter(d => d.posicion === 'DC'),
        derecho: defensores.filter(d => d.posicion === 'ED'),
        izquierdo: defensores.filter(d => d.posicion === 'EI')
      },
      mediocampistas,
      delanteros
    }
  }

  const renderJugador = (jugador, index) => {
    const revelado = jugador.revelado || gameOver
    
    return (
      <div key={index} className="jugador-posicion">
        <div className="jugador-circle">
          {revelado ? (
            <div className="jugador-revelado">
              {jugador.image_url ? (
                <img 
                  src={`http://localhost:8000${jugador.image_url}`} 
                  alt={jugador.jugador_apellido}
                  className="jugador-foto"
                  onError={(e) => {
                    e.target.style.display = 'none'
                    e.target.nextSibling.style.display = 'block'
                  }}
                />
              ) : null}
              <div className="jugador-nombre" style={{display: jugador.image_url ? 'none' : 'block'}}>
                {jugador.jugador_apellido || '?'}
              </div>
              <div className="posicion-small">{jugador.posicion}</div>
            </div>
          ) : (
            <div className="jugador-oculto">
              <div className="posicion-label">{jugador.posicion}</div>
              <div className="interrogacion">?</div>
            </div>
          )}
        </div>
      </div>
    )
  }

  if (loading) {
    return (
      <div className="equipo-game-container">
        <div className="loading">Cargando juego...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="equipo-game-container">
        <div className="error">{error}</div>
      </div>
    )
  }

  if (!gameData) return null

  const formacionData = organizarFormacion()
  const jugadoresRevelados = posiciones.filter(p => p.revelado).length

  return (
    <div className="equipo-game-container">
      <h1>⚽ Equipo Europeo del Día</h1>
      
      {/* Mostrar club actual */}
      {!gameOver && clubActual && (
        <div className="club-actual-section">
          <div className="club-actual-card">
            <div className="club-icon">
              {clubActual.logo_url ? (
                <img 
                  src={`http://localhost:8000${clubActual.logo_url}`} 
                  alt={clubActual.nombre}
                  className="club-logo"
                />
              ) : (
                <div className="club-logo-placeholder">
                  <span className="club-emoji">⚽</span>
                </div>
              )}
            </div>
            <div className="club-info">
              <p className="club-label">Jugador que pasó por:</p>
              <h2 className="club-nombre">{clubActual.nombre}</h2>
            </div>
          </div>
          <div className="progreso-inline">
            <span>{jugadoresRevelados}/11 jugadores</span>
            {entrenadorRevelado && <span className="check-dt">✅ DT</span>}
          </div>
        </div>
      )}
      
      <div className="game-content">
        {/* Campo de fútbol */}
        <div className="campo-futbol">
          <div className="formacion-info">
            <h3>Esquema: {gameData.formacion}</h3>
          </div>

          {/* Portero */}
          <div className="linea portero-linea">
            {formacionData.portero.map((j, i) => renderJugador(j, `po-${i}`))}
          </div>

          {/* Defensores */}
          <div className="linea defensores-linea">
            {formacionData.defensores.izquierdo.map((j, i) => renderJugador(j, `ei-${i}`))}
            {formacionData.defensores.central.map((j, i) => renderJugador(j, `dc-${i}`))}
            {formacionData.defensores.derecho.map((j, i) => renderJugador(j, `ed-${i}`))}
          </div>

          {/* Mediocampistas */}
          <div className="linea mediocampistas-linea">
            {formacionData.mediocampistas.map((j, i) => renderJugador(j, `mc-${i}`))}
          </div>

          {/* Delanteros */}
          <div className="linea delanteros-linea">
            {formacionData.delanteros.map((j, i) => renderJugador(j, `del-${i}`))}
          </div>

          {/* Entrenador */}
          <div className="entrenador-section">
            <div className="entrenador-box">
              <div className="posicion-label">DT</div>
              {entrenadorRevelado || gameOver ? (
                <div className="entrenador-nombre">{gameData.entrenador_apellido}</div>
              ) : (
                <div className="entrenador-oculto">?</div>
              )}
            </div>
          </div>
        </div>

        {/* Panel derecho */}
        <div className="panel-derecho">
          <div className="stats-header">
            <h3>{gameData.formacion}</h3>
            <div className="stats-counters">
              <div className="counter">
                <span className="counter-value">{jugadoresRevelados}/11</span>
                <span className="counter-label">Jugadores</span>
              </div>
              <div className="counter">
                <span className="counter-value">{entrenadorRevelado ? '1' : '0'}/1</span>
                <span className="counter-label">DT</span>
              </div>
            </div>
          </div>
          
          <div className="jugadores-grid">
            {posiciones.map((p, i) => (
              <div key={i} className={`jugador-card ${p.revelado || gameOver ? 'revelado' : 'oculto'}`}>
                <div className="card-posicion">{p.posicion}</div>
                <div className="card-nombre">
                  {p.revelado || gameOver ? p.jugador_apellido : '?'}
                </div>
              </div>
            ))}
            
            <div className={`jugador-card dt-card ${entrenadorRevelado || gameOver ? 'revelado' : 'oculto'}`}>
              <div className="card-posicion">DT</div>
              <div className="card-nombre">
                {entrenadorRevelado || gameOver ? gameData.entrenador_apellido : '?'}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Controles */}
      <div className="controles">
        <form onSubmit={handleSubmit} className="input-form">
          <input
            type="text"
            value={guess}
            onChange={(e) => setGuess(e.target.value)}
            placeholder="APELLIDO DEL JUGADOR"
            className="input-guess"
            disabled={gameOver}
          />
          <button type="submit" disabled={gameOver} className="btn-enviar">
            ENVIAR
          </button>
        </form>

        <div className="botones">
          <button 
            onClick={() => {
              setGameOver(true)
              const newPosiciones = posiciones.map(p => ({ ...p, revelado: true }))
              setPosiciones(newPosiciones)
              setEntrenadorRevelado(true)
              setMensaje('Te rendiste. Aquí está el equipo completo.')
            }} 
            disabled={gameOver} 
            className="btn-rendirse"
          >
            RENDIRSE
          </button>
        </div>

        {mensaje && (
          <div className={`mensaje ${mensaje.includes('✅') ? 'success' : 'error'}`}>
            {mensaje}
          </div>
        )}
      </div>
    </div>
  )
}

export default EquipoNacional
