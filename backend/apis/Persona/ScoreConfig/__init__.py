# ./backend/apis/Persona/ScoreConfig/_init_.py
from fastapi import APIRouter
from .persona_config import router as persona_config_router
from .persona_score_details import router as persona_score_router

router = APIRouter()

router.include_router(persona_config_router)
router.include_router(persona_score_router)