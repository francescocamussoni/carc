import { Link } from 'react-router-dom'
import '../styles/HomePage.css'

function HomePage() {
  const games = [
    {
      id: 'equipo-nacional',
      title: 'Equipo Nacional',
      description: 'Adivina los 11 jugadores argentinos del equipo del día',
      icon: '🇦🇷',
      path: '/equipo-nacional',
      color: '#76b9ff'
    },
    {
      id: 'equipo-internacional',
      title: 'Equipo Internacional',
      description: 'Descubre los jugadores internacionales que pasaron por Central',
      icon: '🌎',
      path: '/equipo-internacional',
      color: '#4a90e2'
    },
    {
      id: 'orbita',
      title: 'Órbita del Día',
      description: 'Identifica los jugadores más destacados bajo un técnico canalla',
      icon: '⚽',
      path: '/orbita',
      color: '#003f7f'
    }
  ]

  return (
    <div className="home-page">
      <div className="hero-section">
        <div className="logo-hero">
          <span className="logo-shield-large">🔵⚪🔵</span>
        </div>
        <h1 className="hero-title">
          Bienvenido a <span className="highlight">carc.io</span>
        </h1>
        <p className="hero-subtitle">Rosario Central</p>
        <p className="hero-description">
          ¡Desafía tus conocimientos sobre el Club Atlético Rosario Central! 
          Juega a los juegos diarios y demuestra que sos un verdadero canalla.
        </p>
      </div>

      <div className="games-grid">
        {games.map((game) => (
          <Link 
            key={game.id} 
            to={game.path} 
            className="game-card"
            style={{ borderTop: `5px solid ${game.color}` }}
          >
            <div className="game-icon">{game.icon}</div>
            <h2 className="game-title">{game.title}</h2>
            <p className="game-description">{game.description}</p>
            <div className="game-footer">
              <span className="play-button">Jugar →</span>
            </div>
          </Link>
        ))}
      </div>

      <div className="info-section">
        <div className="info-card">
          <h3>🎮 Juegos Diarios</h3>
          <p>Nuevos desafíos cada día a medianoche</p>
        </div>
        <div className="info-card">
          <h3>📊 Datos Reales</h3>
          <p>Información obtenida de Transfermarkt</p>
        </div>
        <div className="info-card">
          <h3>🏆 Desafío Canalla</h3>
          <p>Pon a prueba tu conocimiento sobre Central</p>
        </div>
      </div>

      <div className="about-section">
        <h2>Sobre carc.io</h2>
        <p>
          Esta aplicación web te permite disfrutar de diferentes juegos 
          basados en datos reales de los jugadores y técnicos que pasaron por 
          Rosario Central. Cada juego se renueva diariamente, ¡así que volvé 
          todos los días para seguir jugando!
        </p>
      </div>
    </div>
  )
}

export default HomePage
