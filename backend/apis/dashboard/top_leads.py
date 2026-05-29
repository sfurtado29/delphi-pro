from fastapi import APIRouter, HTTPException, Query
from db import get_conn
import logging

router = APIRouter()

@router.get("/top-leads")
def get_top_leads(year: int = Query(..., description="The year to filter leads")):
    conn = get_conn()
    cur = conn.cursor(dictionary=True)

    try:
        # Call procedure with only YEAR
        cur.callproc("Usp_get_top_leads_by_year", (year,))

        top_leads = []
        for result in cur.stored_results():
            top_leads = result.fetchall()

        return {"leads": top_leads}

    except Exception as e:
        logging.error(f"Error fetching top leads: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch top leads")
    finally:
        cur.close()
        conn.close()
