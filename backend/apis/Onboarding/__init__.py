# /Onboarding/__init__.py
from fastapi import APIRouter
from .enrichment import router as enrichment_router
from .profile_routes import router as profile_router

# Combine onboarding sub-routers so `app.include_router(onboarding_router)` in main
# registers both enrichment endpoints and profile endpoints.
router = APIRouter()
router.include_router(enrichment_router)
router.include_router(profile_router)
