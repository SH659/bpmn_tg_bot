from fastapi import APIRouter

from .diagrams import router as diagrams_router

api_router = APIRouter()
api_router.include_router(diagrams_router, prefix="/diagrams", tags=["diagrams"])
