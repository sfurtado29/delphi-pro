# backend/apis/leadscores/filters/get_call_rating.py
from fastapi import APIRouter, HTTPException
from db import get_conn
import logging

router = APIRouter()

@router.get("/call-rating")
def get_call_rating():
    conn = None
    cur = None

    try:
        conn = get_conn()
        cur = conn.cursor(dictionary=True)

        cur.execute("""
            SELECT QAcallrating_id AS id,
                   QAcallrating_desc AS label
            FROM Mst_tblqualityaudit_callrating
            WHERE Isactive = b'1'
        """)

        rows = cur.fetchall() or []

        call_ratings = [
            {"id": r["id"], "label": r["label"]}
            for r in rows
        ]

        return {
            "count": len(call_ratings),
            "data": call_ratings
        }

    except Exception:
        logging.exception("get_call_rating failed")
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch call rating"
        )

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()