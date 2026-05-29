# backend/apis/leadscores/filters/get_industries.py
from fastapi import APIRouter, HTTPException
from db import get_conn
import logging

router = APIRouter()

@router.get("/industries")
def get_industries():
    try:
        conn = get_conn()
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT Standard_industry_id AS id,
                   Standard_industry_desc AS label
            FROM Mst_tblstandardindustry
            WHERE Isactive = b'1'
            ORDER BY Standard_industry_desc;
        """)
        rows = cur.fetchall() or []
        industries = [{"id": r["id"], "label": r["label"]} for r in rows]
        return {"industries": industries}
    except Exception:
        logging.exception("get_industries failed")
        raise HTTPException(status_code=500, detail="Failed to fetch industries")
    finally:
        try:
            cur.close()
            conn.close()
        except:
            pass
