# backend/apis/leadscores/scoring/__init__.py
from fastapi import APIRouter
from .scoring_config import router as scoring_router

router = APIRouter(prefix="/scoring")
router.include_router(scoring_router)
