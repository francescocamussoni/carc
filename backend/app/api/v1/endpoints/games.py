"""
Game endpoints
"""
from fastapi import APIRouter, HTTPException, Path
from typing import Dict, Any
from app.schemas.game import (
    GameResponse,
    EquipoDelDiaGame,
    OrbitaGame,
    GameGuess,
    GameResult
)
from app.services.game_generator import game_generator_service
import difflib


router = APIRouter()


@router.get("/equipo-nacional", response_model=GameResponse)
async def get_equipo_nacional():
    """Get Equipo Nacional del Día"""
    try:
        game = game_generator_service.generate_equipo_nacional()
        return GameResponse(
            success=True,
            game_type="equipo_nacional",
            game_id=game.game_id,
            fecha=game.fecha,
            data=game.model_dump(),
            mensaje="Adivina los 11 jugadores del equipo"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/equipo-internacional", response_model=GameResponse)
async def get_equipo_internacional():
    """Get Equipo Internacional del Día"""
    try:
        game = game_generator_service.generate_equipo_internacional()
        return GameResponse(
            success=True,
            game_type="equipo_internacional",
            game_id=game.game_id,
            fecha=game.fecha,
            data=game.model_dump(),
            mensaje="Adivina los 11 jugadores internacionales del equipo"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/orbita", response_model=GameResponse)
async def get_orbita():
    """Get Órbita del Día"""
    try:
        game = game_generator_service.generate_orbita_del_dia()
        return GameResponse(
            success=True,
            game_type="orbita",
            game_id=game.game_id,
            fecha=game.fecha,
            data=game.model_dump(),
            mensaje=f"Adivina los jugadores con {game.modo_juego.replace('_', ' ')} en {game.competencia}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/verify", response_model=GameResult)
async def verify_guess(guess: GameGuess):
    """Verify a player guess"""
    try:
        game_type = guess.game_type
        respuesta = guess.respuesta.strip().lower()
        
        # Generate the game again (deterministic based on date)
        if game_type == "equipo_nacional":
            game = game_generator_service.generate_equipo_nacional()
            
            # Check if guess matches any player (by apellido or nombre completo)
            match_found = None
            for jugador in game.jugadores:
                if _similar_name(respuesta, jugador.apellido) or _similar_name(respuesta, jugador.nombre_completo):
                    match_found = jugador
                    break
            
            if match_found:
                return GameResult(
                    correcto=True,
                    mensaje=f"¡Correcto! {match_found.nombre_completo} - {match_found.posicion}",
                    jugador_revelado={
                        "nombre": match_found.nombre_completo,
                        "posicion": match_found.posicion,
                        "image_url": match_found.image_url
                    },
                    game_over=False,
                    victoria=False
                )
            else:
                return GameResult(
                    correcto=False,
                    mensaje="Incorrecto. Intenta con otro jugador.",
                    game_over=False,
                    victoria=False
                )
            
        elif game_type == "equipo_internacional":
            game = game_generator_service.generate_equipo_internacional()
            
            match_found = None
            for jugador in game.jugadores:
                if _similar_name(respuesta, jugador.apellido) or _similar_name(respuesta, jugador.nombre_completo):
                    match_found = jugador
                    break
            
            if match_found:
                return GameResult(
                    correcto=True,
                    mensaje=f"¡Correcto! {match_found.nombre_completo} - {match_found.posicion}",
                    jugador_revelado={
                        "nombre": match_found.nombre_completo,
                        "posicion": match_found.posicion,
                        "nacionalidad": match_found.nacionalidad,
                        "image_url": match_found.image_url
                    },
                    game_over=False,
                    victoria=False
                )
            else:
                return GameResult(
                    correcto=False,
                    mensaje="Incorrecto. Intenta con otro jugador.",
                    game_over=False,
                    victoria=False
                )
            
        elif game_type == "orbita":
            game = game_generator_service.generate_orbita_del_dia()
            
            # Check if the guess matches any orbital element
            matches = []
            for elemento in game.elementos_orbitales:
                if _similar_name(respuesta, elemento.nombre):
                    matches.append(elemento.nombre)
            
            if matches:
                return GameResult(
                    correcto=True,
                    mensaje=f"¡Correcto! {matches[0]}",
                    elementos_revelados=matches,
                    game_over=False,
                    victoria=False
                )
            else:
                return GameResult(
                    correcto=False,
                    mensaje="Incorrecto. Intenta de nuevo.",
                    game_over=False,
                    victoria=False
                )
        else:
            raise HTTPException(status_code=400, detail="Tipo de juego inválido")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list", response_model=Dict[str, Any])
async def list_available_games():
    """List all available games"""
    return {
        "games": [
            {
                "id": "equipo_nacional",
                "nombre": "Equipo Nacional del Día",
                "descripcion": "Adivina los 11 jugadores del equipo argentino",
                "endpoint": "/api/v1/games/equipo-nacional"
            },
            {
                "id": "equipo_internacional",
                "nombre": "Equipo Internacional del Día",
                "descripcion": "Adivina los 11 jugadores internacionales",
                "endpoint": "/api/v1/games/equipo-internacional"
            },
            {
                "id": "orbita",
                "nombre": "Órbita del Día",
                "descripcion": "Adivina los jugadores dirigidos por un técnico",
                "endpoint": "/api/v1/games/orbita"
            }
        ]
    }


def _similar_name(guess: str, correct: str, threshold: float = 0.7) -> bool:
    """Check if two names are similar enough"""
    guess = guess.lower().strip()
    correct = correct.lower().strip()
    
    # Exact match
    if guess == correct:
        return True
    
    # Check if guess is contained in correct name or vice versa
    if guess in correct or correct in guess:
        return True
    
    # Use difflib for fuzzy matching
    similarity = difflib.SequenceMatcher(None, guess, correct).ratio()
    return similarity >= threshold
