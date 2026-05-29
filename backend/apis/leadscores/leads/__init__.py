# backend/apis/leadscores/leads/__init__.py
from fastapi import APIRouter
from .get_campaign_leads import router as campaign_leads_router
from .get_lead_detail import router as lead_detail_router

router = APIRouter(prefix="/leads")

router.include_router(campaign_leads_router)
router.include_router(lead_detail_router)
