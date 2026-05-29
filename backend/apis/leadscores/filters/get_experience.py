# backend/apis/leadscores/filters/get_experience.py
from fastapi import APIRouter, HTTPException, Query
from db import get_conn
import logging

router = APIRouter()

@router.get("/experience")
def get_experience(
    q: str = Query(None),
    limit: int = Query(1000)
):
    conn = None
    cur = None

    try:
        conn = get_conn()
        cur = conn.cursor(dictionary=True)

        if limit <= 0:
            limit = 1000
        if limit > 5000:
            limit = 5000

        sql = """
            SELECT DISTINCT Tenurity AS label
            FROM tblleads_masterlist
            WHERE Isdelete = b'0'
              AND Tenurity IS NOT NULL
              AND TRIM(Tenurity) <> ''
              AND TRIM(Tenurity) REGEXP '^[A-Za-z0-9 ]+$'
             
        """

        params = []

        if q:
            sql += " AND LOWER(Tenurity) LIKE LOWER(%s)"
            params.append(f"%{q}%")

        sql += " ORDER BY label LIMIT %s"
        params.append(limit)

        cur.execute(sql, params)
        rows = cur.fetchall() or []

        data = [{"id": r["label"], "label": r["label"]} for r in rows]

        return {"count": len(data), "data": data}

    except Exception:
        logging.exception("get_experience failed")
        raise HTTPException(status_code=500, detail="Failed to fetch experience")

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
