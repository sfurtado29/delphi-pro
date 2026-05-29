# backend/apis/leadscores/filters/__init__.py
from fastapi import APIRouter

from .get_countries import router as countries_router
from .get_industries import router as industries_router
from .get_job_levels import router as job_levels_router
from .get_job_functions import router as job_functions_router
from .get_job_titles import router as job_titles_router
from .get_employee_sizes import router as employee_sizes_router
from .get_revenue_sizes import router as revenue_sizes_router
from .get_campaigns import router as campaigns_router
from .get_qa_status import router as qa_status_router
from .get_lead_type import router as lead_type_router
from .get_lead_source import router as lead_source_router
from .get_brands import router as brands_router
from .get_experience import router as experience_router
from .get_call_engagement import router as call_engagement_router
from .get_call_rating import router as call_rating_router
from .get_call_status import router as call_status_router

router = APIRouter(prefix="/filters")

router.include_router(countries_router)
router.include_router(industries_router)
router.include_router(job_levels_router)
router.include_router(job_functions_router)
router.include_router(job_titles_router)
router.include_router(employee_sizes_router)
router.include_router(revenue_sizes_router)
router.include_router(campaigns_router)
router.include_router(qa_status_router)
router.include_router(lead_type_router)
router.include_router(lead_source_router)
router.include_router(brands_router)
router.include_router(experience_router)
router.include_router(call_engagement_router)
router.include_router(call_rating_router)
router.include_router(call_status_router)
