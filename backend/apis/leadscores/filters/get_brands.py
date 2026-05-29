# backend/apis/leadscores/filters/get_brands.py
from fastapi import APIRouter, HTTPException, Query
from db import get_conn
import logging

router = APIRouter()

@router.get("/brands")
def get_brands(industry_id: int = Query(...)):
    """
    Returns brands linked to selected industry through:
    Leads → Engaged Leads → Campaigns → Clients → Brands
    """

    conn = None
    cur = None

    try:
        conn = get_conn()
        cur = conn.cursor(dictionary=True)

        cur.execute("""
            SELECT DISTINCT
                b.Brand_id AS id,
                b.Brand_name AS label
            FROM tblleads_masterlist lm
            JOIN tblengaged_leads el
                ON el.Lead_id = lm.Lead_id
            JOIN Mst_tblclient_campaigns cc
                ON cc.Campaign_key_id = el.Campaign_key_id
            JOIN Mst_tblclient_brands b
                ON b.Client_id = cc.Client_id
            WHERE lm.Standard_industry_id = %s
              AND b.Brand_name REGEXP '^[A-Za-z]'
              AND b.Isactive = b'1'
            ORDER BY b.Brand_name ASC;
        """, (industry_id,))

        rows = cur.fetchall() or []
        return {"brands": rows}

    except Exception:
        logging.exception("get_brands failed")
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch brands for industry"
        )

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
