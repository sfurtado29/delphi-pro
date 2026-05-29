# backend/apis/dashboard/monthly_stats.py
from fastapi import APIRouter, Query, HTTPException
from db import get_conn
import logging

router = APIRouter()

@router.get("/monthly-leads")
def get_monthly_leads(year: int = Query(...)):
    conn = get_conn()
    cur = conn.cursor(dictionary=True)

    try:
        cur.callproc("Usp_get_monthly_lead_count", [year])

        stats = []
        for result in cur.stored_results():
            stats = result.fetchall()

        return {"monthly_counts": stats}

    except Exception as e:
        logging.error(f"Monthly lead error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()
