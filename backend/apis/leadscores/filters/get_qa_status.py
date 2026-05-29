# backend/apis/leadscores/filters/get_qa_statuses.py

from fastapi import APIRouter, HTTPException
from db import get_conn
import logging

router = APIRouter()

@router.get("/qa-statuses")
def get_qa_statuses():
    """
    Returns:
      { "qa_statuses": [ { "id": <QAstatus_id>, "label": <QAstatus_desc> } ] }
    """
    conn = None
    cur = None
    try:
        conn = get_conn()
        cur = conn.cursor(dictionary=True)

        cur.execute("""
            SELECT
                QAstatus_id AS id,
                QAstatus_desc AS label
            FROM Mst_tblqualityaudit_status
            WHERE Isactive = b'1'
            ORDER BY QAstatus_desc
        """)

        rows = cur.fetchall() or []
        qa_statuses = [{"id": r["id"], "label": r["label"]} for r in rows]

        return {"qa_statuses": qa_statuses}

    except Exception:
        logging.exception("get_qa_statuses failed")
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch QA statuses"
        )

    finally:
        try:
            if cur:
                cur.close()
            if conn:
                conn.close()
        except Exception:
            pass
