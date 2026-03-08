import { Link } from 'react-router-dom'
import '../styles/HomePage.css'
import { BACKEND_URL, CLOUDFRONT_URL, IS_PRODUCTION } from '../services/api'

// Helper para obtener URL base correcta
const BASE_URL = IS_PRODUCTION ? CLOUDFRONT_URL : BACKEND_URL
const IMAGES_PATH = IS_PRODUCTION ? '/images' : '/api/v1/static'

function HomePage() {
  const games = [
    {
      id: 'equipo-nacional',
      title: 'Equipo Nacional',
      description: 'Adiviná los 11 jugadores que pasaron por clubes argentinos',
      icon: '🇦🇷',
      image: `${BASE_URL}${IMAGES_PATH}/otras/ruben.jpg`,
      path: '/equipo-nacional',
      color: '#003DA5' // Azul Central
    },
    {
      id: 'equipo-europeo',
      title: 'Equipo Europeo',
      description: 'Adiviná los 11 jugadores que pasaron por clubes europeos',
      icon: '🇪🇺',
      image: `${BASE_URL}${IMAGES_PATH}/otras/di_maria.jpg`,
      path: '/equipo-europeo',
      color: '#FFD100' // Amarillo Central
    },
    {
      id: 'equipo-latinoamericano',
      title: 'Equipo Latinoamericano',
      description: 'Adiviná los 11 jugadores que pasaron por clubes latinoamericanos',
      icon: '🌎',
      image: `${BASE_URL}${IMAGES_PATH}/otras/bauza.webp`,
      path: '/equipo-latinoamericano',
      color: '#003DA5' // Azul Central
    },
    {
      id: 'equipo-clasico',
      title: 'Equipo Clásico',
      description: 'Adiviná la formación de Central en un clásico rosarino',
      icon: '⚔️',
      image: `${BASE_URL}${IMAGES_PATH}/otras/coudet.jpg`,
      path: '/clasico-del-dia',
      color: '#FFD100' // Amarillo Central
    },
    {
      id: 'trayectoria-dia',
      title: 'Trayectoria del Día',
      description: 'Completa la carrera de un jugador que jugó en el nuestro',
      icon: '🛤️',
      image: `${BASE_URL}${IMAGES_PATH}/otras/abreu.jpg`,
      path: null, // PRONTO
      color: '#003DA5', // Azul Central
      comingSoon: true
    },
    {
      id: 'orbita-dia',
      title: 'Órbita del Día',
      description: 'Ordená jugadores según la consigna',
      icon: '🌐',
      image: `${BASE_URL}${IMAGES_PATH}/otras/jonas.jpg`,
      path: null, // PRONTO
      color: '#FFD100', // Amarillo Central
      comingSoon: true
    }
  ]

  return (
    <div className="home-page">

      <div className="games-grid">
        {games.map((game) => {
          const CardWrapper = game.comingSoon ? 'div' : Link
          const cardProps = game.comingSoon 
            ? { className: "game-card game-card-disabled", style: { borderTop: `5px solid ${game.color}` } }
            : { to: game.path, className: "game-card", style: { borderTop: `5px solid ${game.color}` } }

          return (
            <CardWrapper 
              key={game.id} 
              {...cardProps}
            >
              <div className="game-icon">
                {game.image ? (
                  <img 
                    src={game.image} 
                    alt={game.title} 
                    className={`game-icon-image game-icon-${game.id}`}
                    loading="eager"
                  />
                ) : (
                  game.icon
                )}
              </div>
              <h2 className="game-title">{game.title}</h2>
              <p className="game-description">{game.description}</p>
              <div className="game-footer">
                {game.comingSoon ? (
                  <span className="coming-soon-badge">🔜 PRONTO</span>
                ) : (
                  <span className="play-button">Jugar →</span>
                )}
              </div>
            </CardWrapper>
          )
        })}
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
          <p>Poné a prueba tu conocimiento sobre Central</p>
        </div>
      </div>

      <div className="about-section">
        <h2>Sobre rosariocentral.io</h2>
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
