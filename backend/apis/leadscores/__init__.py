# backend/apis/leadscores/__init__.py
from fastapi import APIRouter

from .filters import router as filters_router
from .leads import router as leads_router
from .scoring import router as scoring_router
router = APIRouter(
    prefix="/leadscores",
    tags=["LeadScoring"]
)

router.include_router(filters_router)
router.include_router(leads_router)
router.include_router(scoring_router)
