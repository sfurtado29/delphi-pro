# apis/Persona/__init__.py
from fastapi import APIRouter
from .GeneratePersona import router as generate_persona_router
from .Persona_csv_export import export_persona_leads_csv

router = APIRouter()

router.include_router(generate_persona_router)
router.include_router(export_persona_leads_csv)


