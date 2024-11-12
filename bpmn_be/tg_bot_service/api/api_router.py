from fastapi import APIRouter

from .tg_bot import router as tg_bot_router

api_router = APIRouter()
api_router.include_router(tg_bot_router, prefix="/bot/tg", tags=["tg"])
