import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';
// Backend base URL without /api/v1 for static files
export const BACKEND_URL = API_BASE_URL.replace('/api/v1', '');
// CloudFront URL for production (HTTPS) - rosariocentral.io
export const CLOUDFRONT_URL = 'https://rosariocentral.io';
// Check if we're in production (HTTPS)
export const IS_PRODUCTION = window.location.protocol === 'https:';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Games API
export const gamesAPI = {
  // Get Equipo Nacional del Día
  getEquipoNacional: async () => {
    const response = await api.get('/games/equipo-nacional');
    return response.data;
  },

  // Get Equipo Europeo del Día
  getEquipoEuropeo: async () => {
    const response = await api.get('/games/equipo-europeo');
    return response.data;
  },

  // Get Equipo Latinoamericano del Día
  getEquipoLatinoamericano: async () => {
    const response = await api.get('/games/equipo-latinoamericano');
    return response.data;
  },

  // Verify guess
  verifyGuess: async (gameId, gameType, respuesta, tiempoJugado = null) => {
    const response = await api.post('/games/verify', {
      game_id: gameId,
      game_type: gameType,
      respuesta: respuesta,
      tiempo_jugado: tiempoJugado,
    });
    return response.data;
  },

  // Confirm position selection for multi-position player
  confirmarPosicion: async (gameId, posicion) => {
    const response = await api.post('/games/confirmar-posicion', {
      game_id: gameId,
      posicion: posicion,
    });
    return response.data;
  },
  
  confirmarJugador: async (gameId, nombreJugador) => {
    const response = await api.post('/games/confirmar-jugador', {
      game_id: gameId,
      nombre_jugador: nombreJugador,
    });
    return response.data;
  },

  // Get hints for current club
  obtenerPista: async (gameId) => {
    const response = await api.get(`/games/pista/${gameId}`);
    return response.data;
  },

  // Reveal random player (EASY mode only)
  revelarJugador: async (gameId) => {
    const response = await api.post(`/games/revelar-jugador/${gameId}`);
    return response.data;
  },

  // Get list of available games
  listGames: async () => {
    const response = await api.get('/games/list');
    return response.data;
  },

  // Clásico del Día
  getClasicoDelDia: async () => {
    const response = await api.get('/games/clasico-del-dia');
    return response.data;
  },

  verifyClasicoAnswer: async (guess) => {
    const response = await api.post('/games/clasico/verify', {
      game_id: guess.game_id,
      game_type: guess.game_type,
      respuesta: guess.respuesta
    });
    return response.data;
  },

  getClasicoHint: async (gameId) => {
    const response = await api.get(`/games/clasico/pista/${gameId}`);
    return response.data;
  },

  revelarJugadorClasicoAPI: async (gameId) => {
    const response = await api.post(`/games/clasico/revelar-jugador/${gameId}`);
    return response.data;
  },

  verifyClasicoResultado: async (gameId, resultado) => {
    const response = await api.post('/games/clasico/verificar-resultado', {
      game_id: gameId,
      resultado: resultado,
    });
    return response.data;
  },
};

// Helper to get image URL
export const getImageUrl = (path) => {
  if (!path) return null;
  if (path.startsWith('http')) return path;
  
  // Si estamos en HTTPS (producción), usar CloudFront para las imágenes
  if (IS_PRODUCTION) {
    // Convertir /api/v1/static/jugadores/X.jpg -> /images/jugadores/X.jpg
    const imagePath = path.replace('/api/v1/static/', '/images/');
    return `${CLOUDFRONT_URL}${imagePath}`;
  }
  
  // En desarrollo (HTTP), usar el backend directamente
  return `${BACKEND_URL}${path}`;
};

export default api;
