import { useState, useEffect } from 'react'
import { gamesAPI } from '../services/api'
import '../styles/EquipoGame.css'

function EquipoGame({ gameType, title }) {
  const [gameData, setGameData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [guess, setGuess] = useState('')
  const [clubActual, setClubActual] = useState(null)
  const [posiciones, setPosiciones] = useState([])
  const [entrenadorRevelado, setEntrenadorRevelado] = useState(false)
  const [entrenadorNombre, setEntrenadorNombre] = useState(null) // Nombre del DT adivinado
  const [entrenadorImageUrl, setEntrenadorImageUrl] = useState(null) // Foto del DT
  const [mensaje, setMensaje] = useState('')
  const [gameOver, setGameOver] = useState(false)
  const [mostrarPista, setMostrarPista] = useState(false)
  const [mostrarSelectorPosicion, setMostrarSelectorPosicion] = useState(false)
  const [posicionesDisponibles, setPosicionesDisponibles] = useState([])
  const [jugadorPendiente, setJugadorPendiente] = useState(null)
  const [mostrarSelectorJugador, setMostrarSelectorJugador] = useState(false)
  const [jugadoresDisponibles, setJugadoresDisponibles] = useState([])
  const [apellidoBuscado, setApellidoBuscado] = useState('')

  useEffect(() => {
    fetchGame()
  }, [])

  const fetchGame = async () => {
    try {
      setLoading(true)
      let data
      
      // Llamar a la API según el tipo de juego
      switch(gameType) {
        case 'nacional':
          data = await gamesAPI.getEquipoNacional()
          break
        case 'europeo':
          data = await gamesAPI.getEquipoEuropeo()
          break
        case 'latinoamericano':
          data = await gamesAPI.getEquipoLatinoamericano()
          break
        default:
          throw new Error('Tipo de juego no válido')
      }
      
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
      const gameTypeMap = {
        'nacional': 'equipo_nacional',
        'europeo': 'equipo_europeo',
        'latinoamericano': 'equipo_latinoamericano'
      }
      
      const result = await gamesAPI.verifyGuess(
        gameData.game_id,
        gameTypeMap[gameType],
        guess
      )

      if (result.correcto) {
        // ✅ NUEVO: Check if requires player selection (multiple players with same surname)
        if (result.requiere_seleccion_jugador && result.jugadores_disponibles) {
          setMensaje(`✅ ${result.mensaje}`)
          setJugadoresDisponibles(result.jugadores_disponibles)
          setApellidoBuscado(guess)
          setMostrarSelectorJugador(true)
          setMostrarPista(false)
        }
        // Check if requires position selection
        else if (result.requiere_seleccion && result.posiciones_disponibles) {
          setMensaje(`✅ ${result.mensaje}`)
          setJugadorPendiente(result.jugador_revelado)
          setPosicionesDisponibles(result.posiciones_disponibles)
          setMostrarSelectorPosicion(true)
          setMostrarPista(false)
        } else {
          // Normal flow - position assigned automatically
          setMensaje(`✅ ${result.mensaje}`)
          setMostrarPista(false)
          
          // Update positions from result
          if (result.posicion_asignada) {
            const newPosiciones = [...posiciones]
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
            setEntrenadorNombre(result.jugador_revelado.nombre) // Guardar nombre del DT
            setEntrenadorImageUrl(result.jugador_revelado.image_url) // Guardar foto del DT
          }

          // Check victory
          const revelados = posiciones.filter(p => p.revelado).length
          if (revelados >= 10 && entrenadorRevelado) {
            setGameOver(true)
            setMensaje('🎉 ¡Felicitaciones! Completaste el equipo')
          }
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

  const handleSeleccionJugador = async (nombreJugador) => {
    try {
      const result = await gamesAPI.confirmarJugador(gameData.game_id, nombreJugador)
      
      if (result.correcto) {
        // ✅ Ahora puede requerir selección de posición O asignar directamente
        if (result.requiere_seleccion && result.posiciones_disponibles) {
          setMensaje(`✅ ${result.mensaje}`)
          setJugadorPendiente(result.jugador_revelado)
          setPosicionesDisponibles(result.posiciones_disponibles)
          setMostrarSelectorPosicion(true)
          setMostrarSelectorJugador(false)
        } else {
          setMensaje(`✅ ${result.mensaje}`)
          
          // Update positions from result
          if (result.posicion_asignada) {
            const newPosiciones = [...posiciones]
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

          // Check victory
          const revelados = posiciones.filter(p => p.revelado).length
          if (revelados >= 10 && entrenadorRevelado) {
            setGameOver(true)
            setMensaje('🎉 ¡Felicitaciones! Completaste el equipo')
          }
          
          // Close selector
          setMostrarSelectorJugador(false)
          setJugadoresDisponibles([])
        }
      }
      
      setGuess('')
    } catch (err) {
      console.error('Error confirmando jugador:', err)
      setMensaje('Error al confirmar el jugador')
      setTimeout(() => setMensaje(''), 3000)
    }
  }

  const handleSeleccionPosicion = async (posicion) => {
    try {
      const result = await gamesAPI.confirmarPosicion(gameData.game_id, posicion)
      
      if (result.correcto) {
        setMensaje(`✅ ${result.mensaje}`)
        
        // Update positions from result
        if (result.posicion_asignada) {
          const newPosiciones = [...posiciones]
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

        // Check victory
        const revelados = posiciones.filter(p => p.revelado).length
        if (revelados >= 10 && entrenadorRevelado) {
          setGameOver(true)
          setMensaje('🎉 ¡Felicitaciones! Completaste el equipo')
        }
      }
      
      // Close selector
      setMostrarSelectorPosicion(false)
      setPosicionesDisponibles([])
      setJugadorPendiente(null)
      setGuess('')
    } catch (err) {
      console.error('Error confirmando posición:', err)
      setMensaje('Error al confirmar la posición')
      setTimeout(() => setMensaje(''), 3000)
    }
  }

  const handlePista = () => {
    setMostrarPista(!mostrarPista)
  }

  const handleRendirse = () => {
    setGameOver(true)
    const newPosiciones = posiciones.map(p => ({ ...p, revelado: true }))
    setPosiciones(newPosiciones)
    setEntrenadorRevelado(true)
    setEntrenadorNombre(gameData.entrenador_nombre_completo) // Mostrar DT del juego
    setMensaje('Te rendiste. Aquí está el equipo completo.')
    setMostrarPista(false)
    setMostrarSelectorPosicion(false) // Cerrar selector si está abierto
  }

  const organizarFormacion = () => {
    if (!posiciones || posiciones.length === 0) {
      return { portero: [], defensores: { central: [], derecho: [], izquierdo: [] }, mediocampistas: [], mediocampistasOfensivos: [], delanteros: [] }
    }
    
    const portero = posiciones.filter(p => p.posicion === 'PO')
    const defensores = posiciones.filter(p => ['DC', 'ED', 'EI'].includes(p.posicion))
    const mediocampistas = posiciones.filter(p => ['MC', 'MD', 'MI'].includes(p.posicion))
    const mediocampistasOfensivos = posiciones.filter(p => p.posicion === 'MO')
    const delanteros = posiciones.filter(p => p.posicion === 'DEL')

    return {
      portero,
      defensores: {
        central: defensores.filter(d => d.posicion === 'DC'),
        derecho: defensores.filter(d => d.posicion === 'ED'),
        izquierdo: defensores.filter(d => d.posicion === 'EI')
      },
      mediocampistas,
      mediocampistasOfensivos,
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
      <div className="game-content-two-columns">
        {/* COLUMNA 1: CLUB + CONTROLES */}
        <div className="columna-izquierda">
          {/* Club arriba */}
          {!gameOver && clubActual && (
            <div className="club-section">
              <div className="club-icon-large">
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
              <div className="club-info-vertical">
                <p className="club-label">JUGADOR QUE PASÓ POR:</p>
                <h2 className="club-nombre">{clubActual.nombre}</h2>
              </div>
              <div className="separador"></div>
              <div className="progreso-vertical">
                <div className="progreso-item">
                  <span className="progreso-numero">{jugadoresRevelados}/11</span>
                  <span className="progreso-texto">JUGADORES</span>
                </div>
                <div className="progreso-item">
                  <span className="progreso-numero">{entrenadorRevelado ? '1' : '0'}/1</span>
                  <span className="progreso-texto">TÉCNICO</span>
                </div>
              </div>
            </div>
          )}

          {/* Controles debajo */}
          <div className="controles-section">
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
                onClick={handlePista}
                disabled={gameOver} 
                className="btn-pista"
              >
                💡 PISTA
              </button>
              <button 
                onClick={handleRendirse}
                disabled={gameOver} 
                className="btn-rendirse"
              >
                RENDIRSE
              </button>
            </div>

            {mostrarPista && (
              <div className="pista-container">
                <div className="pista-header">
                  <h4>💡 PISTA</h4>
                  <button className="pista-close" onClick={() => setMostrarPista(false)}>✕</button>
                </div>
                <div className="pista-content">
                  <p>Este jugador jugó en {clubActual?.nombre || 'este club'} y actualmente tiene {21 + Math.floor(Math.random() * 15)} años de edad.</p>
                  <p className="pista-hint">Pista: Su apellido tiene {5 + Math.floor(Math.random() * 5)} letras.</p>
                </div>
              </div>
            )}

            {mensaje && (
              <div className={`mensaje ${mensaje.includes('✅') ? 'success' : 'error'}`}>
                {mensaje}
              </div>
            )}

            {mostrarSelectorJugador && (
              <div className="selector-posicion-container">
                <div className="selector-posicion-header">
                  <h4>👥 Hay {jugadoresDisponibles.length} jugadores con ese apellido. Elegí uno:</h4>
                </div>
                <div className="selector-posicion-botones">
                  {jugadoresDisponibles.map((jugador) => (
                    <button
                      key={jugador}
                      onClick={() => handleSeleccionJugador(jugador)}
                      className="btn-posicion btn-jugador"
                    >
                      {jugador}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {mostrarSelectorPosicion && (
              <div className="selector-posicion-container">
                <div className="selector-posicion-header">
                  <h4>⚽ Elegí la posición para {jugadorPendiente?.apellido || jugadorPendiente?.nombre}</h4>
                </div>
                <div className="selector-posicion-botones">
                  {posicionesDisponibles.map((pos) => (
                    <button
                      key={pos}
                      onClick={() => handleSeleccionPosicion(pos)}
                      className="btn-posicion"
                    >
                      {pos}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* COLUMNA 2: CAMPO DE FÚTBOL (MÁS GRANDE) */}
        <div className="columna-centro">
          <div className="campo-futbol">
            <div className="formacion-info">
              <h3>ESQUEMA: {gameData.formacion}</h3>
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

            {/* Mediocampistas Ofensivos (4-3-2-1) */}
            {formacionData.mediocampistasOfensivos.length > 0 && (
              <div className="linea mediocampistas-ofensivos-linea">
                {formacionData.mediocampistasOfensivos.map((j, i) => renderJugador(j, `mo-${i}`))}
              </div>
            )}

            {/* Delanteros */}
            <div className="linea delanteros-linea">
              {formacionData.delanteros.map((j, i) => renderJugador(j, `del-${i}`))}
            </div>

            {/* Entrenador */}
            <div className="entrenador-section">
              <div className="entrenador-box">
                <div className="posicion-label">DT</div>
                {entrenadorRevelado || gameOver ? (
                  <>
                    {entrenadorImageUrl ? (
                      <div className="entrenador-circle">
                        <img 
                          src={`http://localhost:8000${entrenadorImageUrl}`} 
                          alt={entrenadorNombre || gameData.entrenador_apellido}
                          className="entrenador-foto"
                          onError={(e) => {
                            e.target.style.display = 'none'
                          }}
                        />
                      </div>
                    ) : null}
                    <div className="entrenador-nombre" style={{display: entrenadorImageUrl ? 'none' : 'block'}}>
                      {entrenadorNombre || gameData.entrenador_apellido}
                    </div>
                  </>
                ) : (
                  <div className="entrenador-oculto">?</div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* ✅ NUEVO: Modal de Victoria */}
      {gameOver && mensaje.includes('Felicitaciones') && (
        <div className="modal-victoria">
          <div className="victoria-contenido">
            <div className="victoria-escudo">
              <img 
                src="http://localhost:8000/api/v1/static/clubes/argentina/rosario_central.png"
                alt="Rosario Central"
                className="escudo-victoria"
              />
            </div>
            <h2 className="victoria-titulo">🎉 ¡FELICITACIONES! 🎉</h2>
            <p className="victoria-mensaje">¡Completaste el equipo!</p>
            <button 
              onClick={() => window.location.reload()} 
              className="btn-jugar-de-nuevo"
            >
              🔄 JUGAR DE NUEVO
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

export default EquipoGame
