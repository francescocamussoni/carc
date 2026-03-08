import { useState } from 'react'
import '../styles/DifficultySelector.css'
import { BACKEND_URL, CLOUDFRONT_URL, IS_PRODUCTION } from '../services/api'

const BASE_URL = IS_PRODUCTION ? CLOUDFRONT_URL : BACKEND_URL
const IMAGES_PATH = IS_PRODUCTION ? '/images' : '/api/v1/static'

function DifficultySelector({ onSelect, onSelectDifficulty, gameTitle, onClose }) {
  const [hoveredDiff, setHoveredDiff] = useState(null)
  
  // Use onSelect if provided, otherwise use onSelectDifficulty (backwards compatibility)
  const handleSelect = onSelect || onSelectDifficulty
  
  console.log('DifficultySelector rendered, handler:', handleSelect ? 'exists' : 'missing')

  const difficulties = [
    {
      id: 'facil',
      name: 'POTRERO',
      image: `${BASE_URL}${IMAGES_PATH}/otras/palma.webp`,
      color: '#2ecc71',
      features: [
        '3 pistas disponibles',
        '3 revelaciones de jugador',
        'Sin límite de tiempo'
      ]
    },
    {
      id: 'intermedio',
      name: 'CLÁSICO',
      image: `${BASE_URL}${IMAGES_PATH}/otras/miguel.png`,
      color: '#f39c12',
      features: [
        '3 pistas disponibles',
        'Sin límite de tiempo'
      ]
    },
    {
      id: 'dificil',
      name: 'HAZAÑA',
      image: `${BASE_URL}${IMAGES_PATH}/otras/petaco.avif`,
      color: '#e74c3c',
      features: [
        '3 pistas disponibles',
        '⏱️ 60 segundos para completar'
      ]
    }
  ]

  return (
    <div className="difficulty-overlay">
      <div className="difficulty-modal">
        {onClose && (
          <button className="difficulty-close" onClick={onClose} aria-label="Cerrar">
            ✕
          </button>
        )}
        <div className="difficulty-header">
          <h1>⚽ SELECCIONÁ DIFICULTAD</h1>
          <p>{gameTitle || 'Elegí cómo querés jugar hoy'}</p>
        </div>

        <div className="difficulty-options">
          {difficulties.map((diff) => (
            <div
              key={diff.id}
              className={`difficulty-card ${hoveredDiff === diff.id ? 'hovered' : ''}`}
              onMouseEnter={() => setHoveredDiff(diff.id)}
              onMouseLeave={() => setHoveredDiff(null)}
              onClick={() => {
                console.log('Card clicked:', diff.id)
                handleSelect(diff.id)
              }}
              style={{ '--diff-color': diff.color }}
            >
              <div className="difficulty-icon">
                <img 
                  src={diff.image} 
                  alt={diff.name} 
                  className="difficulty-image"
                  loading="eager"
                  decoding="async"
                />
              </div>
              <h2 className="difficulty-name">{diff.name}</h2>
              
              <div className="difficulty-features">
                {diff.features.map((feature, idx) => (
                  <div key={idx} className="feature-item">
                    <span className="feature-bullet"></span>
                    <span className="feature-text">{feature}</span>
                  </div>
                ))}
              </div>

              <button 
                className="difficulty-btn"
                onClick={(e) => {
                  e.stopPropagation()
                  console.log('Button clicked:', diff.id)
                  handleSelect(diff.id)
                }}
              >
                JUGAR
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default DifficultySelector
