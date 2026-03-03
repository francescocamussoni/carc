import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom'
import HomePage from './pages/HomePage'
import EquipoNacional from './pages/EquipoNacional'
import EquipoEuropeo from './pages/EquipoEuropeo'
import EquipoLatinoamericano from './pages/EquipoLatinoamericano'
import './styles/App.css'

function App() {
  return (
    <Router>
      <div className="app rosario-central">
        <nav className="navbar">
          <div className="nav-container">
            <Link to="/" className="nav-logo">
              <div className="logo-container">
                <img 
                  src="http://localhost:8000/api/v1/static/clubes/argentina/rosario_central.png" 
                  alt="Rosario Central" 
                  className="logo-shield"
                />
                <div>
                  <h1>carc.io</h1>
                  <span className="nav-subtitle">Rosario Central</span>
                </div>
              </div>
            </Link>
            <div className="nav-menu">
              <Link to="/" className="nav-link">Inicio</Link>
              <Link to="/equipo-nacional" className="nav-link">Equipo Nacional</Link>
              <Link to="/equipo-europeo" className="nav-link">Equipo Europeo</Link>
              <Link to="/equipo-latinoamericano" className="nav-link">Equipo Latinoamericano</Link>
            </div>
          </div>
        </nav>

        <main className="main-content">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/equipo-nacional" element={<EquipoNacional />} />
            <Route path="/equipo-europeo" element={<EquipoEuropeo />} />
            <Route path="/equipo-latinoamericano" element={<EquipoLatinoamericano />} />
          </Routes>
        </main>

        <footer className="footer">
          <p>© 2026 carc.io - Rosario Central</p>
          <p>Datos obtenidos de Transfermarkt</p>
        </footer>
      </div>
    </Router>
  )
}

export default App
