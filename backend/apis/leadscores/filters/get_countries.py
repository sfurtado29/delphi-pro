# backend/apis/leadscores/filters/get_countries.py
from fastapi import APIRouter, HTTPException
from db import get_conn
import logging

router = APIRouter()

@router.get("/countries")
def get_countries():
    conn = None
    cur = None
    try:
        conn = get_conn()
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT
              Location_id AS id,
              Location_desc AS label,
              Location_short_desc AS short,
              Location_phone_code AS phone_code,
              Plocation_id AS parent_id,
              Location_type AS type
            FROM Mst_tbllocationelements
            WHERE (Location_type = 'Country' OR Plocation_id IS NULL)
              AND Isactive = b'1'
            ORDER BY Location_desc
        """)
        rows = cur.fetchall() or []
        return {"countries": rows}
    except Exception as e:
        logging.exception("get_countries failed")
        raise HTTPException(status_code=500, detail="Failed to fetch countries")
    finally:
        try:
            if cur:
                cur.close()
            if conn:
                conn.close()
        except:
            pass
