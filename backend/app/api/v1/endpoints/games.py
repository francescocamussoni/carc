"""
Game endpoints
"""
from fastapi import APIRouter, HTTPException, Path
from typing import Dict, Any
from app.schemas.game import (
    GameResponse,
    EquipoDelDiaGame,
    GameGuess,
    GameResult,
    PosicionSeleccionada,
    JugadorSeleccionado
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
            victoria=result.get('victoria', False),
            requiere_seleccion=result.get('requiere_seleccion', False),
            posiciones_disponibles=result.get('posiciones_disponibles'),
            requiere_seleccion_jugador=result.get('requiere_seleccion_jugador', False),
            jugadores_disponibles=result.get('jugadores_disponibles')
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pista/{game_id}")
async def obtener_pista(game_id: str):
    """
    Get hints for the current club
    
    Returns:
    - Primera letra del apellido
    - Posición principal
    - Otro club donde jugó (si disponible)
    """
    try:
        result = game_generator_service.obtener_pista(game_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/revelar-jugador/{game_id}")
async def revelar_jugador_aleatorio(game_id: str):
    """
    Reveal a random player that meets club and position requirements.
    Only available in EASY mode.
    
    Returns:
    - Jugador revelado (apellido, nombre, posición, foto)
    - Posiciones actualizadas
    - Nuevo club
    - Estado del juego
    """
    try:
        result = game_generator_service.revelar_jugador_aleatorio(game_id)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/confirmar-posicion", response_model=GameResult)
async def confirmar_posicion(seleccion: PosicionSeleccionada):
    """Confirm position choice for a multi-position player"""
    try:
        result = game_generator_service.confirmar_posicion(
            seleccion.game_id,
            seleccion.posicion
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


@router.post("/confirmar-jugador", response_model=GameResult)
async def confirmar_jugador(seleccion: JugadorSeleccionado):
    """Confirm player choice when multiple players match the same surname"""
    try:
        result = game_generator_service.confirmar_jugador(
            seleccion.game_id,
            seleccion.nombre_jugador
        )
        
        return GameResult(
            correcto=result.get('correcto', False),
            mensaje=result.get('mensaje', ''),
            jugador_revelado=result.get('jugador_revelado'),
            posicion_asignada=result.get('posicion_asignada'),
            nuevo_club=result.get('nuevo_club'),
            game_over=result.get('game_over', False),
            victoria=result.get('victoria', False),
            requiere_seleccion=result.get('requiere_seleccion', False),
            posiciones_disponibles=result.get('posiciones_disponibles')
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/clasico-del-dia")
async def get_clasico_del_dia():
    """Get Clásico del Día (Rosario Central vs Newell's Old Boys)"""
    try:
        game = game_generator_service.generate_clasico_del_dia()
        return {
            "success": True,
            "game_type": "clasico",
            "game_id": game["game_id"],
            "fecha": game["fecha"],
            "data": game,
            "mensaje": "Adivina la formación del clásico rosarino"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/clasico/verify")
async def verify_clasico_answer(guess: GameGuess):
    """
    Verify a player/coach/referee answer for the classic match game
    Uses same format as other games
    """
    try:
        result = game_generator_service.verificar_respuesta_clasico(
            game_id=guess.game_id,
            respuesta=guess.respuesta
        )
        return GameResult(
            correcto=result.get('correcto', False),
            mensaje=result.get('mensaje', ''),
            jugador_revelado=result.get('jugador_revelado'),
            posicion_asignada=result.get('posicion_asignada'),
            entrenador_revelado=result.get('entrenador_revelado'),
            arbitro_revelado=result.get('arbitro_revelado'),
            game_over=result.get('game_over', False),
            victoria=result.get('victoria', False)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/clasico/pista/{game_id}")
async def get_clasico_hint(game_id: str = Path(..., description="Game ID")):
    """
    Get a hint for a non-revealed player in the classic match
    Returns first letter of surname and another club where they played
    """
    try:
        hint = game_generator_service.obtener_pista_clasico(game_id)
        return hint
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/clasico/revelar-jugador/{game_id}")
async def revelar_jugador_clasico(game_id: str):
    """
    Reveal a random non-revealed player in the classic match
    Only available in EASY mode
    """
    try:
        result = game_generator_service.revelar_jugador_clasico(game_id)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/clasico/verificar-resultado")
async def verificar_resultado_clasico(request: Dict[str, Any]):
    """
    Verify the match result
    
    Args:
        request: Dict with 'game_id' and 'resultado'
    """
    try:
        game_id = request.get("game_id")
        resultado = request.get("resultado")
        
        if not game_id or not resultado:
            raise HTTPException(status_code=400, detail="game_id and resultado are required")
        
        result = game_generator_service.verificar_resultado_clasico(game_id, resultado)
        return result
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
            },
            {
                "id": "clasico",
                "nombre": "Clásico del Día",
                "descripcion": "Adivina la formación de Rosario Central en un clásico vs Newell's Old Boys",
                "endpoint": "/api/v1/games/clasico-del-dia"
            }
        ]
    }
