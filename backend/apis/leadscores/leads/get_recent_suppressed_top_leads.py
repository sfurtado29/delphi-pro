# backend/apis/leadscores/leads/get_recent_suppressed_top_leads.py
from fastapi import APIRouter
from db import get_conn

router = APIRouter()

@router.get("/recent-suppressed-top-leads")
def get_recent_suppressed_top_leads():
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    try:
        cur.callproc("Usp_get_recent_suppressed_top_leads")
        data = []
        for result in cur.stored_results():
            data = result.fetchall()
        return {"leads": data}
    finally:
        cur.close()
        conn.close()
