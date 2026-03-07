import { useState, useEffect } from 'react'
import { gamesAPI } from '../services/api'
import DifficultySelector from './DifficultySelector'
import '../styles/EquipoGame.css'

function ClasicoGame() {
  // Dificultad
  const [mostrarSelectorDificultad, setMostrarSelectorDificultad] = useState(true)
  const [dificultad, setDificultad] = useState(null)
  const [pistasUsadas, setPistasUsadas] = useState(0)
  const [revelacionesUsadas, setRevelacionesUsadas] = useState(0)
  const [tiempoRestante, setTiempoRestante] = useState(60)
  const [timerActivo, setTimerActivo] = useState(false)
  
  // Game state
  const [gameData, setGameData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [guess, setGuess] = useState('')
  const [posiciones, setPosiciones] = useState([])
  const [entrenador, setEntrenador] = useState(null)
  const [resultado, setResultado] = useState(null)
  const [arbitro, setArbitro] = useState(null)
  const [mensaje, setMensaje] = useState('')
  const [gameOver, setGameOver] = useState(false)
  const [mostrarPista, setMostrarPista] = useState(false)
  const [pistasReales, setPistasReales] = useState(null)

  // Resultado input
  const [resultadoInput, setResultadoInput] = useState('')
  const [mostrarResultadoInput, setMostrarResultadoInput] = useState(false)

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
    
    if (diffSelected === 'dificil') {
      setTimerActivo(true)
    }
  }

  const fetchGame = async () => {
    try {
      setLoading(true)
      const data = await gamesAPI.getClasicoDelDia()
      
      setGameData(data.data)
      setPosiciones(data.data.posiciones || [])
      setEntrenador(data.data.entrenador)
      setResultado(data.data.resultado)
      setArbitro(data.data.arbitro)
      setLoading(false)
    } catch (err) {
      console.error('Error loading clásico:', err)
      setError('Error al cargar el clásico del día')
      setLoading(false)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!guess.trim() || gameOver) return

    try {
      const result = await gamesAPI.verifyClasicoAnswer({
        game_id: gameData.game_id,
        game_type: 'clasico',
        respuesta: guess
      })

      if (result.correcto) {
        setMensaje(`✅ ${result.mensaje}`)
        setMostrarPista(false)
        
        // Update jugador revelado
        if (result.jugador_revelado) {
          const newPosiciones = [...posiciones]
          const idx = newPosiciones.findIndex(
            p => p.jugador_apellido === result.jugador_revelado.apellido && !p.revelado
          )
          if (idx !== -1) {
            newPosiciones[idx].revelado = true
            setPosiciones(newPosiciones)
          }
        }

        // Update entrenador revelado
        if (result.entrenador_revelado) {
          setEntrenador(result.entrenador_revelado)
        }

        // Update arbitro revelado
        if (result.arbitro_revelado) {
          setArbitro(result.arbitro_revelado)
        }

        // Check victory
        if (result.game_over) {
          setGameOver(true)
          setMensaje('🎉 ¡Felicitaciones! Completaste el clásico del día')
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

  const handleObtenerPista = async () => {
    if (pistasUsadas >= 3) {
      setMensaje('⚠️ Ya usaste todas las pistas disponibles')
      setTimeout(() => setMensaje(''), 3000)
      return
    }

    try {
      const pista = await gamesAPI.getClasicoHint(gameData.game_id)
      
      if (pista.error) {
        setMensaje(`⚠️ ${pista.error}`)
        setTimeout(() => setMensaje(''), 3000)
        return
      }

      setPistasReales(pista)
      setMostrarPista(true)
      setPistasUsadas(prev => prev + 1)
    } catch (err) {
      console.error('Error getting hint:', err)
      setMensaje('Error al obtener pista')
      setTimeout(() => setMensaje(''), 3000)
    }
  }

  const handleRevelarJugador = async () => {
    if (dificultad !== 'facil') {
      setMensaje('⚠️ Solo disponible en modo Potrero')
      setTimeout(() => setMensaje(''), 3000)
      return
    }

    if (revelacionesUsadas >= 3) {
      setMensaje('⚠️ Ya usaste todas las revelaciones disponibles')
      setTimeout(() => setMensaje(''), 3000)
      return
    }

    try {
      const result = await gamesAPI.revelarJugadorClasicoAPI(gameData.game_id)
      
      if (result.error) {
        setMensaje(`⚠️ ${result.error}`)
        setTimeout(() => setMensaje(''), 3000)
        return
      }

      setMensaje(`✨ ${result.mensaje}`)
      setMostrarPista(false)
      setRevelacionesUsadas(prev => prev + 1)

      // Update based on tipo
      if (result.tipo === 'jugador' && result.jugador_revelado) {
        const newPosiciones = [...posiciones]
        const idx = newPosiciones.findIndex(
          p => p.jugador_apellido === result.jugador_revelado.apellido && !p.revelado
        )
        if (idx !== -1) {
          newPosiciones[idx].revelado = true
          setPosiciones(newPosiciones)
        }
      } else if (result.tipo === 'entrenador' && result.entrenador_revelado) {
        setEntrenador(result.entrenador_revelado)
      }

      // Check victory
      if (result.game_over) {
        setGameOver(true)
        setMensaje('🎉 ¡Felicitaciones! Completaste el clásico del día')
      }

      setTimeout(() => {
        if (!result.game_over) setMensaje('')
      }, 3000)
    } catch (err) {
      console.error('Error revealing player:', err)
      setMensaje('Error al revelar jugador')
      setTimeout(() => setMensaje(''), 3000)
    }
  }

  const handleVerificarResultado = async () => {
    if (!resultadoInput.trim()) return

    try {
      const result = await gamesAPI.verifyClasicoResultado(gameData.game_id, resultadoInput)
      
      if (result.correcto) {
        setMensaje(`✅ ${result.mensaje}`)
        setResultado(result.resultado_revelado)
        setMostrarResultadoInput(false)
        setResultadoInput('')
      } else {
        setMensaje(`❌ ${result.mensaje}`)
      }

      setTimeout(() => setMensaje(''), 3000)
    } catch (err) {
      console.error('Error verifying resultado:', err)
      setMensaje('Error al verificar resultado')
      setTimeout(() => setMensaje(''), 3000)
    }
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
    
    const esquema = gameData?.esquema || '4-3-3'
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
    
    // Debug: Log image URL when revealed
    if (revelado && jugador.image_url) {
      console.log(`🖼️ Jugador revelado: ${jugador.jugador_apellido}, URL: ${jugador.image_url}`)
    }
    
    return (
      <div key={index} className="jugador-posicion">
        <div className="jugador-circle">
          {revelado ? (
            <div className="jugador-revelado">
              {jugador.image_url && (
                <img 
                  src={jugador.image_url} 
                  alt={jugador.jugador_apellido}
                  className="jugador-foto"
                  onLoad={(e) => {
                    console.log(`✅ Imagen cargada: ${jugador.jugador_apellido}`)
                  }}
                  onError={(e) => {
                    console.error(`❌ Error cargando imagen: ${jugador.jugador_apellido}, URL: ${jugador.image_url}`)
                    e.target.style.display = 'none'
                  }}
                />
              )}
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

  if (mostrarSelectorDificultad) {
    return <DifficultySelector onSelectDifficulty={handleSelectDifficulty} />
  }

  if (loading) {
    return (
      <div className="equipo-game-container">
        <div className="loading">Cargando clásico...</div>
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
        {/* COLUMNA 1: INFO DEL CLÁSICO + CONTROLES */}
        <div className="columna-izquierda">
          {/* Info del Clásico arriba */}
          {!(gameOver && mensaje.includes('Felicitaciones')) && (
            <div className="club-section">
              <div className="club-icon-large">
                <img 
                  src="http://localhost:8000/api/v1/static/clubes/argentina/rosario_central.png" 
                  alt="Rosario Central"
                  className="club-logo"
                />
              </div>
              <div className="club-info-vertical">
                <p className="club-label">CLÁSICO ROSARINO</p>
                <h2 className="club-nombre">{gameData.local} vs {gameData.visitante}</h2>
                <p className="club-label" style={{marginTop: '0.5rem'}}>{gameData.fecha}</p>
                <p className="club-label">{gameData.competicion}</p>
              </div>
              <div className="separador"></div>
              <div className="progreso-compacto">
                <div className="progreso-item">
                  <span className="progreso-numero">{jugadoresRevelados}/11</span>
                  <span className="progreso-texto">JUGADORES</span>
                </div>
                <div className="progreso-item">
                  <span className="progreso-numero">{entrenador?.revelado ? '1' : '0'}/1</span>
                  <span className="progreso-texto">TÉCNICO</span>
                </div>
                <div className="progreso-item">
                  <span className="progreso-numero">{resultado?.revelado ? '✅' : '❌'}</span>
                  <span className="progreso-texto">RESULTADO</span>
                </div>
                <div className="progreso-item">
                  <span className="progreso-numero">{arbitro?.revelado ? '✅' : '❌'}</span>
                  <span className="progreso-texto">ÁRBITRO</span>
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
                  src="http://localhost:8000/api/v1/static/clubes/argentina/rosario_central.png"
                  alt="Rosario Central"
                  className="escudo-victoria-panel"
                />
              </div>
              <h2 className="victoria-titulo-panel">🎉 ¡FELICITACIONES! 🎉</h2>
              <p className="victoria-subtitulo-panel">Completaste el clásico del día</p>
              <div className="victoria-stats-panel">
                <div className="stat-item-panel">
                  <span className="stat-label-panel">Jugadores</span>
                  <span className="stat-value-panel">{jugadoresRevelados}/11</span>
                </div>
                <div className="stat-item-panel">
                  <span className="stat-label-panel">Técnico</span>
                  <span className="stat-value-panel">1/1</span>
                </div>
              </div>
            </div>
          ) : (
            <div className="controles-section">
              {/* Input para adivinar */}
              {!gameOver && (
                <form onSubmit={handleSubmit} className="guess-form-vertical">
                  <label className="input-label">APELLIDO DEL JUGADOR</label>
                  <input
                    type="text"
                    value={guess}
                    onChange={(e) => setGuess(e.target.value)}
                    placeholder="Ingresa apellido..."
                    className="guess-input-vertical"
                    autoFocus
                  />
                  <button type="submit" className="btn-primary-full">
                    ENVIAR
                  </button>
                </form>
              )}

              {/* Botón Adivinar Resultado */}
              {!resultado?.revelado && !gameOver && (
                <div className="accion-extra">
                  <button 
                    onClick={() => setMostrarResultadoInput(!mostrarResultadoInput)}
                    className="btn-secondary-full"
                  >
                    {mostrarResultadoInput ? '❌ CANCELAR' : '⚽ ADIVINAR RESULTADO'}
                  </button>
                  
                  {mostrarResultadoInput && (
                    <div className="input-extra-form">
                      <input
                        type="text"
                        value={resultadoInput}
                        onChange={(e) => setResultadoInput(e.target.value)}
                        placeholder="Ej: 2-1"
                        className="input-extra"
                      />
                      <button 
                        onClick={handleVerificarResultado}
                        className="btn-verificar"
                      >
                        VERIFICAR
                      </button>
                    </div>
                  )}
                </div>
              )}

              {/* Pistas y Revelación */}
              {!gameOver && (
                <div className="acciones-rapidas">
                  <button 
                    onClick={handleObtenerPista}
                    className="btn-accion"
                    disabled={pistasUsadas >= 3}
                  >
                    💡 PISTA ({pistasUsadas}/3)
                  </button>

                  {dificultad === 'facil' && (
                    <button 
                      onClick={handleRevelarJugador}
                      className="btn-accion btn-revelar"
                      disabled={revelacionesUsadas >= 3}
                    >
                      ✨ REVELAR ({revelacionesUsadas}/3)
                    </button>
                  )}
                </div>
              )}

              {/* Pista Display */}
              {mostrarPista && pistasReales && (
                <div className="pista-panel">
                  <h4 className="pista-titulo">💡 PISTA</h4>
                  <div className="pista-contenido">
                    <p><strong>Letra:</strong> {pistasReales.letra_apellido}</p>
                    <p><strong>Posición:</strong> {pistasReales.posicion_principal}</p>
                    {pistasReales.otro_club && (
                      <p><strong>Otro club:</strong> {pistasReales.otro_club}</p>
                    )}
                  </div>
                </div>
              )}

              {/* Mensaje */}
              {mensaje && (
                <div className={`mensaje-feedback ${
                  mensaje.startsWith('✅') || mensaje.startsWith('✨') ? 'mensaje-exito' : 
                  mensaje.startsWith('❌') ? 'mensaje-error' : 
                  mensaje.startsWith('⚠️') ? 'mensaje-warning' : 
                  mensaje.startsWith('🎉') ? 'mensaje-exito' : 'mensaje-info'
                }`}>
                  {mensaje}
                </div>
              )}
            </div>
          )}
        </div>

        {/* COLUMNA 2: CAMPO TÁCTICO */}
        <div className="columna-centro">
          <div className="campo-futbol">
            <div className="formacion-info">
              <h3>ESQUEMA: {gameData.esquema}</h3>
            </div>
            {/* Portero */}
            <div className="linea portero-linea">
              {formacionData.portero.map((jugador, idx) => renderJugador(jugador, idx))}
            </div>

            {/* Defensores */}
            <div className="linea defensores-linea">
              {formacionData.defensores.izquierdo.map((jugador, idx) => renderJugador(jugador, `ei-${idx}`))}
              {formacionData.defensores.central.map((jugador, idx) => renderJugador(jugador, `dc-${idx}`))}
              {formacionData.defensores.derecho.map((jugador, idx) => renderJugador(jugador, `ed-${idx}`))}
            </div>

            {/* Mediocampistas */}
            <div className="linea mediocampistas-linea">
              {formacionData.mediocampistas.map((jugador, idx) => renderJugador(jugador, `mc-${idx}`))}
            </div>

            {/* Mediocampistas Ofensivos */}
            {formacionData.mediocampistasOfensivos.length > 0 && (
              <div className="linea mediocampistas-ofensivos-linea">
                {formacionData.mediocampistasOfensivos.map((jugador, idx) => renderJugador(jugador, `mo-${idx}`))}
              </div>
            )}

            {/* Delanteros */}
            <div className="linea delanteros-linea">
              {formacionData.delanteros.map((jugador, idx) => renderJugador(jugador, `del-${idx}`))}
            </div>

            {/* Entrenador */}
            <div className="entrenador-section">
              <div className="entrenador-box">
                <div className="posicion-label">DT</div>
                {entrenador?.revelado || gameOver ? (
                  <>
                    {entrenador?.image_url ? (
                      <div className="entrenador-circle">
                        <img 
                          src={entrenador.image_url} 
                          alt={entrenador.apellido}
                          className="entrenador-foto"
                          onError={(e) => {
                            e.target.style.display = 'none'
                          }}
                        />
                      </div>
                    ) : null}
                    <div className="entrenador-nombre" style={{display: entrenador?.image_url ? 'none' : 'block'}}>
                      {entrenador?.apellido || '???'}
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
  )
}

export default ClasicoGame
