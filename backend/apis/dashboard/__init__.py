# backend/apis/dashboard/__init__.py
from fastapi import APIRouter
from .monthly_stats import router as monthly_router
from .top_leads import router as top_leads_router
from .get_icp_dashboard import router as icp_dashboard_router
from .get_propensity_dashboard import router as propensity_dashboard_router

router = APIRouter(prefix="/dashboard")

router.include_router(monthly_router)
router.include_router(top_leads_router)
router.include_router(propensity_dashboard_router)
router.include_router(icp_dashboard_router)
