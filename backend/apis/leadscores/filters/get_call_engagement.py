# backend/apis/leadscores/filters/get_call_engagement.py
from fastapi import APIRouter, HTTPException
from db import get_conn
import logging

router = APIRouter()

@router.get("/call-engagement")
def get_call_engagement():
    conn = None
    cur = None

    try:
        conn = get_conn()
        cur = conn.cursor(dictionary=True)

        cur.execute("""
            SELECT CallEngagement_id AS id,
                   Call_engagement AS label
            FROM Mst_tblqualityaudit_callEngagement
            WHERE Isactive = b'1'
        """)

        rows = cur.fetchall() or []

        call_engagements = [
            {"id": r["id"], "label": r["label"]}
            for r in rows
        ]

        return {
            "count": len(call_engagements),
            "data": call_engagements
        }

    except Exception:
        logging.exception("get_call_engagement failed")
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch call engagement"
        )

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()