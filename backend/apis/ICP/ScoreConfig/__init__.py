# backend/apis/ICP/ScoreConfig/__init__.py
from fastapi import APIRouter

# Import routers from local files
from .icp_config import router as icp_config_router
from .icp_score_details import router as icp_score_router

# Main ICP router
router = APIRouter()

# Include ICP configuration APIs
router.include_router(
    icp_config_router,   # routes like /icp-config/parameters, /icp-config/values/{parameter_id}
    prefix="",           # no extra prefix; frontend path: /leadscores/scoring/icp-config/...
    tags=["ICP Configuration"]
)

# Include ICP scoring detail APIs (read-only)
router.include_router(
    icp_score_router,    # routes like /icp-score-details/{lead_id}
    prefix="",           # no extra prefix
    tags=["ICP Scoring Details"]
)
