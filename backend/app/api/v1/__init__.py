from fastapi import APIRouter
from .endpoints import games

api_router = APIRouter()

# Include game endpoints
api_router.include_router(games.router, prefix="/games", tags=["games"])

__all__ = ["api_router"]
