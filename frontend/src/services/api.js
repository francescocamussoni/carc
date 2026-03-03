import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

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

  // Get list of available games
  listGames: async () => {
    const response = await api.get('/games/list');
    return response.data;
  },
};

// Helper to get image URL
export const getImageUrl = (path) => {
  if (!path) return null;
  if (path.startsWith('http')) return path;
  return `http://localhost:8000${path}`;
};

export default api;
