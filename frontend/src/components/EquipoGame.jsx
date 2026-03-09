import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { gamesAPI, BACKEND_URL, CLOUDFRONT_URL, IS_PRODUCTION, getImageUrl } from '../services/api'
import DifficultySelector from './DifficultySelector'

const BASE_URL = IS_PRODUCTION ? CLOUDFRONT_URL : BACKEND_URL
const IMAGES_PATH = IS_PRODUCTION ? '/images' : '/api/v1/static'
import '../styles/EquipoGame.css'

function EquipoGame({ gameType, title }) {
  const navigate = useNavigate()
  
  // Dificultad
  const [mostrarSelectorDificultad, setMostrarSelectorDificultad] = useState(true)
  const [dificultad, setDificultad] = useState(null)
  const [clubesPorPosicion, setClubesPorPosicion] = useState({}) // Guardar club de la pista por posición
  const [pistasUsadas, setPistasUsadas] = useState(0)
  const [revelacionesUsadas, setRevelacionesUsadas] = useState(0)
  const [tiempoRestante, setTiempoRestante] = useState(60)
  const [timerActivo, setTimerActivo] = useState(false)
  
  // Game state
  const [gameData, setGameData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [guess, setGuess] = useState('')
  const [clubActual, setClubActual] = useState(null)
  const [posiciones, setPosiciones] = useState([])
  const [entrenadorRevelado, setEntrenadorRevelado] = useState(false)
  const [entrenadorNombre, setEntrenadorNombre] = useState(null)
  const [entrenadorImageUrl, setEntrenadorImageUrl] = useState(null)
  const [mensaje, setMensaje] = useState('')
  const [gameOver, setGameOver] = useState(false)
  const [mostrarPista, setMostrarPista] = useState(false)
  const [pistasReales, setPistasReales] = useState(null)
  const [mostrarSelectorPosicion, setMostrarSelectorPosicion] = useState(false)
  const [posicionesDisponibles, setPosicionesDisponibles] = useState([])
  const [jugadorPendiente, setJugadorPendiente] = useState(null)
  const [mostrarSelectorJugador, setMostrarSelectorJugador] = useState(false)
  const [jugadoresDisponibles, setJugadoresDisponibles] = useState([])
  const [apellidoBuscado, setApellidoBuscado] = useState('')
  const [clubEntrenador, setClubEntrenador] = useState(null) // 🔒 Guardar el club con el que se reveló el entrenador

  useEffect(() => {
    if (dificultad) {
      fetchGame()
    }
  }, [dificultad])

  // Timer para modo difícil
  useEffect(() => {
    if (dificultad === 'dificil' && timerActivo && tiempoRestante > 0 && !gameOver) {
      const interval = setInterval(() => {
        setTiempoRestante(prev => {
          if (prev <= 1) {
            clearInterval(interval)
            setGameOver(true)
            setMensaje('⏰ ¡Se acabó el tiempo! Perdiste.')
            return 0
          }
          return prev - 1
        })
      }, 1000)
      
      return () => clearInterval(interval)
    }
  }, [dificultad, timerActivo, tiempoRestante, gameOver])

  const handleSelectDifficulty = (diffSelected) => {
    setDificultad(diffSelected)
    setMostrarSelectorDificultad(false)
    
    // Si es difícil, iniciar timer cuando cargue el juego
    if (diffSelected === 'dificil') {
      setTimerActivo(true)
    }
  }

  const handleCloseDifficultySelector = () => {
    navigate('/')
  }

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
              const apellido = result.jugador_revelado.apellido || result.jugador_revelado.nombre.split(' ').pop()
              newPosiciones[idx] = {
                ...newPosiciones[idx],
                revelado: true,
                jugador_nombre: result.jugador_revelado.nombre,
                jugador_apellido: apellido,
                image_url: result.jugador_revelado.image_url,
                club_revelado: clubActual  // 🔒 Guardar el club actual directamente en la posición
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
            setEntrenadorImageUrl(getImageUrl(result.jugador_revelado.image_url)) // Guardar foto del DT
            
            // 🔒 Guardar el club actual para el entrenador
            if (clubActual) {
              setClubEntrenador(clubActual)
            }
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
              const apellido = result.jugador_revelado.apellido || result.jugador_revelado.nombre.split(' ').pop()
              newPosiciones[idx] = {
                ...newPosiciones[idx],
                revelado: true,
                jugador_nombre: result.jugador_revelado.nombre,
                jugador_apellido: apellido,
                image_url: result.jugador_revelado.image_url,
                club_revelado: clubActual  // 🔒 Guardar el club actual directamente en la posición
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
            const apellido = result.jugador_revelado.apellido || result.jugador_revelado.nombre.split(' ').pop()
            newPosiciones[idx] = {
              ...newPosiciones[idx],
              revelado: true,
              jugador_nombre: result.jugador_revelado.nombre,
              jugador_apellido: apellido,
              image_url: result.jugador_revelado.image_url,
              club_revelado: clubActual  // 🔒 Guardar el club actual directamente en la posición
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

  const handlePista = async () => {
    // Verificar si quedan pistas disponibles
    if (pistasUsadas >= 3) {
      setMensaje('❌ Ya usaste las 3 pistas disponibles')
      setTimeout(() => setMensaje(''), 3000)
      return
    }
    
    if (!mostrarPista) {
      // Si no está mostrando la pista, obtenerla del backend
      try {
        const result = await gamesAPI.obtenerPista(gameData.game_id)
        
        if (result.error) {
          setMensaje(`❌ ${result.error}`)
          return
        }
        
        setPistasReales(result.pistas)
        setMostrarPista(true)
        setPistasUsadas(prev => prev + 1) // Incrementar contador
      } catch (error) {
        console.error('Error obteniendo pista:', error)
        setMensaje('❌ Error al obtener pista')
      }
    } else {
      // Si ya está mostrando, solo ocultar
      setMostrarPista(false)
    }
  }

  const handleRendirse = () => {
    setGameOver(true)
    // 🔒 Preservar club_revelado de los jugadores ya revelados
    const newPosiciones = posiciones.map(p => {
      if (p.revelado && p.club_revelado) {
        // Ya estaba revelado, preservar su club
        return { ...p, revelado: true }
      } else {
        // Nuevo revelado, sin club (mostrará Rosario Central como fallback)
        return { ...p, revelado: true }
      }
    })
    setPosiciones(newPosiciones)
    setEntrenadorRevelado(true)
    setEntrenadorNombre(gameData.entrenador_nombre_completo) // Mostrar DT del juego
    setMensaje('Te rendiste. Aquí está el equipo completo.')
    setMostrarPista(false)
    setMostrarSelectorPosicion(false) // Cerrar selector si está abierto
  }

  const handleRevelarJugador = async () => {
    // Solo disponible en modo fácil
    if (dificultad !== 'facil') {
      return
    }
    
    // Verificar si quedan revelaciones disponibles
    if (revelacionesUsadas >= 3) {
      setMensaje('❌ Ya usaste las 3 revelaciones disponibles')
      setTimeout(() => setMensaje(''), 3000)
      return
    }
    
    try {
      const result = await gamesAPI.revelarJugador(gameData.game_id)
      
      if (result.error) {
        setMensaje(`❌ ${result.error}`)
        setTimeout(() => setMensaje(''), 3000)
        return
      }
      
      // 🔒 Actualizar posiciones preservando los club_revelado existentes y agregando al nuevo
      setPosiciones(prevPosiciones => {
        return result.posiciones.map(newPos => {
          // Buscar si esta posición ya existía
          const existingPos = prevPosiciones.find(p => p.posicion === newPos.posicion)
          
          // Si ya estaba revelada, preservar su club_revelado
          if (existingPos?.revelado && existingPos.club_revelado) {
            return {
              ...newPos,
              club_revelado: existingPos.club_revelado
            }
          }
          
          // Si es el jugador recién revelado, guardar el club actual
          if (newPos.revelado && !existingPos?.revelado) {
            return {
              ...newPos,
              club_revelado: clubActual
            }
          }
          
          return newPos
        })
      })
      
      // Actualizar club actual
      if (result.nuevo_club) {
        setClubActual(result.nuevo_club)
      }
      
      // Incrementar contador de revelaciones
      setRevelacionesUsadas(prev => prev + 1)
      
      // Mostrar mensaje
      setMensaje(result.mensaje)
      
      // Si el juego terminó
      if (result.game_over) {
        setGameOver(true)
      }
      
      // Limpiar mensaje después de 3 segundos
      setTimeout(() => setMensaje(''), 3000)
      
    } catch (error) {
      console.error('Error revelando jugador:', error)
      setMensaje('❌ Error al revelar jugador')
      setTimeout(() => setMensaje(''), 3000)
    }
  }

  // Helper function to get club logo path
  const getClubLogoPath = (clubNombre) => {
    if (!clubNombre) return null
    
    // Normalize club name to filename format
    const normalized = clubNombre
      .toLowerCase()
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '') // Remove accents
      .replace(/\s+/g, '_') // Replace spaces with underscores
      .replace(/[^a-z0-9_]/g, '') // Remove special characters
    
    // Try Argentina clubs first, then internacional
    return `${BASE_URL}${IMAGES_PATH}/clubes/argentina/${normalized}.png`
  }

  const organizarFormacion = () => {
    if (!posiciones || posiciones.length === 0) {
      return { portero: [], defensores: { central: [], derecho: [], izquierdo: [] }, mediocampistas: [], mediocampistasOfensivos: [], delanteros: [] }
    }
    
    const portero = posiciones.filter(p => p.posicion === 'PO')
    const defensores = posiciones.filter(p => ['DC', 'ED', 'EI'].includes(p.posicion))
    const delanteros = posiciones.filter(p => p.posicion === 'DEL')
    
    // Organizar mediocampistas según el esquema
    let mediocampistas = []
    let mediocampistasOfensivos = []
    
    const esquema = gameData?.formacion || '4-3-3'
    const lineas = esquema.split('-').length
    
    if (lineas === 4) {
      // Esquemas con 4 líneas (ej: 4-2-3-1, 3-4-1-2)
      // Línea 2: solo MC (pivotes)
      // Línea 3: MO, MI, MD (mediapuntas)
      mediocampistas = posiciones.filter(p => p.posicion === 'MC')
      mediocampistasOfensivos = posiciones.filter(p => ['MO', 'MI', 'MD'].includes(p.posicion))
    } else {
      // Esquemas con 3 líneas (ej: 4-3-3, 4-4-2, 3-5-2)
      // Línea 2: MC, MI, MD todos juntos
      mediocampistas = posiciones.filter(p => ['MC', 'MI', 'MD'].includes(p.posicion))
      mediocampistasOfensivos = posiciones.filter(p => p.posicion === 'MO')
    }

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
    
    // Get club logo - use the club that was saved when this player was revealed
    let clubLogoPath = `${BASE_URL}${IMAGES_PATH}/clubes/argentina/rosario_central.png`
    let clubAlt = 'Rosario Central'
    
    if (revelado && jugador.club_revelado) {
      // 🔒 Usar el club que fue guardado directamente en la posición cuando se reveló
      if (jugador.club_revelado.logo_url) {
        clubLogoPath = `${BASE_URL}${jugador.club_revelado.logo_url.replace('/api/v1/static', IMAGES_PATH)}`
        clubAlt = jugador.club_revelado.nombre
      }
    }
    
    return (
      <div key={index} className="jugador-posicion">
        <div className="jugador-circle">
          {revelado ? (
            <div className="jugador-revelado">
              {jugador.image_url && (
                <img 
                  src={getImageUrl(jugador.image_url)} 
                  alt={jugador.jugador_apellido}
                  className="jugador-foto"
                  onError={(e) => {
                    e.target.style.display = 'none'
                  }}
                />
              )}
              <div className="escudo-jugador">
                <img 
                  src={clubLogoPath}
                  alt={clubAlt}
                  onError={(e) => {
                    // Fallback to Rosario Central if club logo fails
                    e.target.src = `${BASE_URL}${IMAGES_PATH}/clubes/argentina/rosario_central.png`
                  }}
                />
              </div>
              <div className="jugador-nombre">
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

  // Mostrar selector de dificultad antes de cargar el juego
  if (mostrarSelectorDificultad) {
    return (
      <DifficultySelector 
        onSelectDifficulty={handleSelectDifficulty} 
        onClose={handleCloseDifficultySelector}
        gameTitle={title}
      />
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

  // Ya no necesitamos organizarFormacion - usamos posiciones con coordenadas directamente
  // const formacionData = organizarFormacion()
  const jugadoresRevelados = posiciones.filter(p => p.revelado).length

  return (
    <div className="equipo-game-container">
      <div className="game-content-two-columns">
        {/* COLUMNA 1: CLUB + CONTROLES */}
        <div className="columna-izquierda">
          {/* Club arriba - Solo ocultar si es victoria */}
          {!(gameOver && mensaje.includes('Felicitaciones')) && clubActual && (
            <div className="club-section">
              <div className="club-icon-large">
                {clubActual.logo_url ? (
                  <img 
                    src={`${BASE_URL}${clubActual.logo_url.replace('/api/v1/static', IMAGES_PATH)}`} 
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
              
              {/* Timer (modo difícil) */}
              {dificultad === 'dificil' && (
                <div className="timer-container">
                  <div className={`timer ${tiempoRestante <= 10 ? 'timer-urgente' : ''}`}>
                    <span className="timer-icon">⏱️</span>
                    <span className="timer-numero">{tiempoRestante}s</span>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Controles debajo O mensaje de victoria */}
          {gameOver && mensaje.includes('Felicitaciones') ? (
            <div className="victoria-panel">
              <div className="victoria-escudo-panel">
                <img 
                  src={`${BASE_URL}${IMAGES_PATH}/clubes/argentina/rosario_central.png`}
                  alt="Rosario Central"
                  className="escudo-victoria-panel"
                />
              </div>
              <h2 className="victoria-titulo-panel">🎉 ¡FELICITACIONES! 🎉</h2>
              <p className="victoria-mensaje-panel">¡Completaste el equipo!</p>
              <button 
                onClick={() => window.location.reload()} 
                className="btn-jugar-de-nuevo-panel"
              >
                🔄 JUGAR DE NUEVO
              </button>
            </div>
          ) : (
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
                  disabled={gameOver || pistasUsadas >= 3} 
                  className="btn-pista"
                >
                  💡 PISTA ({3 - pistasUsadas})
                </button>
                {dificultad === 'facil' && (
                  <button 
                    onClick={handleRevelarJugador}
                    disabled={gameOver || revelacionesUsadas >= 3}
                    className="btn-revelar"
                  >
                    ✨ REVELAR ({3 - revelacionesUsadas})
                  </button>
                )}
                <button 
                  onClick={handleRendirse}
                  disabled={gameOver} 
                  className="btn-rendirse"
                >
                  RENDIRSE
                </button>
              </div>

              {mostrarPista && pistasReales && (
                <div className="pista-container">
                  <div className="pista-header">
                    <h4>💡 PISTA</h4>
                    <button className="pista-close" onClick={() => setMostrarPista(false)}>✕</button>
                  </div>
                  <div className="pista-content">
                    <p>🔤 <strong>Primera letra:</strong> {pistasReales.letra_inicial}</p>
                    <p>⚽ <strong>Posición:</strong> {pistasReales.posicion}</p>
                    {pistasReales.otro_club && (
                      <p>🏟️ <strong>También jugó en:</strong> {pistasReales.otro_club}</p>
                    )}
                  </div>
                </div>
              )}

              {mensaje && (
                <div className={`mensaje ${mensaje.includes('✅') || mensaje.includes('✨') ? 'success' : 'error'}`}>
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
          )}
        </div>

        {/* COLUMNA 2: CAMPO DE FÚTBOL (MÁS GRANDE) */}
        <div className="columna-centro">
          <div className="campo-futbol">
            <div className="campo-con-dt">
              {/* FORMACIÓN CON POSICIONES ABSOLUTAS */}
              <div className="formacion-container">
                {posiciones.map((jugador, index) => (
                  <div 
                    key={index}
                    className="jugador-posicion-absoluta"
                    style={{
                      left: `${jugador.x || 50}%`,
                      top: `${jugador.y || 50}%`
                    }}
                  >
                    {renderJugador(jugador, index)}
                  </div>
                ))}
              </div>

              {/* SEPARADOR */}
              <div className="dt-separador"></div>

              {/* ENTRENADOR AL COSTADO */}
              <div className="dt-lateral">
                {/* Esquema encima del técnico */}
                <div className="formacion-info-lateral">
                  <h4>ESQUEMA</h4>
                  <p className="esquema-numero">{gameData.formacion}</p>
                </div>
                <div className="entrenador-section">
                  <div className="entrenador-box">
                    <div className="posicion-label">DT</div>
                    {entrenadorRevelado || gameOver ? (
                      <>
                        {entrenadorImageUrl ? (
                          <div className="entrenador-circle">
                            <img 
                              src={entrenadorImageUrl} 
                              alt={entrenadorNombre || gameData.entrenador_apellido}
                              className="entrenador-foto"
                              onError={(e) => {
                                e.target.style.display = 'none'
                              }}
                            />
                            {/* Escudo del club */}
                            {clubEntrenador && clubEntrenador.logo_url && (
                              <div className="escudo-jugador">
                                <img 
                                  src={`${BASE_URL}${clubEntrenador.logo_url.replace('/api/v1/static', IMAGES_PATH)}`}
                                  alt={clubEntrenador.nombre}
                                  onError={(e) => {
                                    e.target.src = `${BASE_URL}${IMAGES_PATH}/clubes/argentina/rosario_central.png`
                                  }}
                                />
                              </div>
                            )}
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
        </div>
      </div>
    </div>
  )
}

export default EquipoGame
