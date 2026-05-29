# backend/apis/leadscores/filters/get_call_rating.py
from fastapi import APIRouter, HTTPException
from db import get_conn
import logging

router = APIRouter()

@router.get("/call-status")
def get_call_status():
    conn = None
    cur = None

    try:
        conn = get_conn()
        cur = conn.cursor(dictionary=True)

        cur.execute("""
            SELECT Callstatus_id AS id,
                   Call_status AS label
            FROM Mst_tblqualityaudit_callstatus
            WHERE Isactive = b'1'
        """)

        rows = cur.fetchall() or []

        call_status = [
            {"id": r["id"], "label": r["label"]}
            for r in rows
        ]

        return {
            "count": len(call_status),
            "data": call_status
        }

    except Exception:
        logging.exception("get_call_status failed")
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch call status"
        )

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()