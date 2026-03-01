"""
Game endpoints
"""
from fastapi import APIRouter, HTTPException, Path
from typing import Dict, Any
from app.schemas.game import (
    GameResponse,
    EquipoDelDiaGame,
    GameGuess,
    GameResult
)
from app.services.game_generator import game_generator_service


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
            mensaje="Adivina los jugadores que pasaron por estos clubes"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/equipo-europeo", response_model=GameResponse)
async def get_equipo_europeo():
    """Get Equipo Europeo del Día"""
    try:
        game = game_generator_service.generate_equipo_europeo()
        return GameResponse(
            success=True,
            game_type="equipo_europeo",
            game_id=game.game_id,
            fecha=game.fecha,
            data=game.model_dump(),
            mensaje="Adivina los jugadores que pasaron por clubes europeos"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/equipo-latinoamericano", response_model=GameResponse)
async def get_equipo_latinoamericano():
    """Get Equipo Latinoamericano del Día"""
    try:
        game = game_generator_service.generate_equipo_latinoamericano()
        return GameResponse(
            success=True,
            game_type="equipo_latinoamericano",
            game_id=game.game_id,
            fecha=game.fecha,
            data=game.model_dump(),
            mensaje="Adivina los jugadores que pasaron por clubes latinoamericanos"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/verify", response_model=GameResult)
async def verify_guess(guess: GameGuess):
    """Verify a player guess - Nueva mecánica"""
    try:
        # Use new verification logic
        result = game_generator_service.verificar_respuesta(
            guess.game_id,
            guess.game_type,
            guess.respuesta
        )
        
        return GameResult(
            correcto=result.get('correcto', False),
            mensaje=result.get('mensaje', ''),
            jugador_revelado=result.get('jugador_revelado'),
            posicion_asignada=result.get('posicion_asignada'),
            nuevo_club=result.get('nuevo_club'),
            game_over=result.get('game_over', False),
            victoria=result.get('victoria', False)
        )
    
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
                "descripcion": "Adivina los 11 jugadores que pasaron por clubes argentinos",
                "endpoint": "/api/v1/games/equipo-nacional"
            },
            {
                "id": "equipo_europeo",
                "nombre": "Equipo Europeo del Día",
                "descripcion": "Adivina los 11 jugadores que pasaron por clubes europeos",
                "endpoint": "/api/v1/games/equipo-europeo"
            },
            {
                "id": "equipo_latinoamericano",
                "nombre": "Equipo Latinoamericano del Día",
                "descripcion": "Adivina los 11 jugadores que pasaron por clubes latinoamericanos",
                "endpoint": "/api/v1/games/equipo-latinoamericano"
            }
        ]
    }
