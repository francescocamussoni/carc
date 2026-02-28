import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom'
import HomePage from './pages/HomePage'
import EquipoNacional from './pages/EquipoNacional'
import EquipoInternacional from './pages/EquipoInternacional'
import OrbitaDelDia from './pages/OrbitaDelDia'
import './styles/App.css'

function App() {
  return (
    <Router>
      <div className="app rosario-central">
        <nav className="navbar">
          <div className="nav-container">
            <Link to="/" className="nav-logo">
              <div className="logo-container">
                <span className="logo-shield">🔵⚪🔵</span>
                <div>
                  <h1>carc.io</h1>
                  <span className="nav-subtitle">Rosario Central</span>
                </div>
              </div>
            </Link>
            <div className="nav-menu">
              <Link to="/" className="nav-link">Inicio</Link>
              <Link to="/equipo-nacional" className="nav-link">Equipo Nacional</Link>
              <Link to="/equipo-internacional" className="nav-link">Equipo Internacional</Link>
              <Link to="/orbita" className="nav-link">Órbita</Link>
            </div>
          </div>
        </nav>

        <main className="main-content">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/equipo-nacional" element={<EquipoNacional />} />
            <Route path="/equipo-internacional" element={<EquipoInternacional />} />
            <Route path="/orbita" element={<OrbitaDelDia />} />
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
