# backend/apis/leadscores/filters/get_job_titles.py
from fastapi import APIRouter, HTTPException, Query
from db import get_conn
import logging

router = APIRouter()

@router.get("/job_titles")
def get_job_titles(q: str = Query(None, description="Search substring (case-insensitive)"),
                   limit: int = Query(1000, description="Max number of titles to return")):
    """
    Returns:
      { "job_titles": [ { "id": "<job title>", "label": "<job title>" }, ... ] }

    Notes:
      - Uses DISTINCT on Job_title from tblleads_masterlist
      - Skips empty job titles and deleted leads (Isdelete = 1)
      - Supports optional substring search (q) and limit.
    """
    conn = None
    cur = None
    try:
        conn = get_conn()
        cur = conn.cursor(dictionary=True)

        # Protect limit
        if limit is None or limit <= 0:
            limit = 1000
        if limit > 5000:
            limit = 5000

        # Build query with optional filter
        if q:
            # Use case-insensitive match. Parameterized query prevents injection.
            sql = """
                SELECT DISTINCT TRIM(Job_title) AS label
                FROM tblleads_masterlist
                WHERE Isdelete = b'0'
                  AND Job_title IS NOT NULL
                  AND TRIM(Job_title) <> ''
                  AND LOWER(Job_title) LIKE LOWER(%s)
                  AND TRIM(Job_title) REGEXP '^[A-Za-z0-9 ]+$'
                ORDER BY label ASC
                LIMIT %s
            """
            params = (f"%{q}%", limit)
        else:
            sql = """
                SELECT DISTINCT TRIM(Job_title) AS label
                FROM tblleads_masterlist
                WHERE Isdelete = b'0'
                  AND Job_title IS NOT NULL
                  AND TRIM(Job_title) <> ''
                  AND TRIM(Job_title) REGEXP '^[A-Za-z]+$'
                ORDER BY label
                LIMIT %s
            """
            params = (limit,)

        cur.execute(sql, params)
        rows = cur.fetchall() or []

        # Map to frontend-friendly shape: id and label (id == label here)
        job_titles = [{"id": r["label"], "label": r["label"]} for r in rows]

        return {"job_titles": job_titles}

    except Exception as e:
        logging.exception("get_job_titles failed")
        raise HTTPException(status_code=500, detail="Failed to fetch job titles")
    finally:
        try:
            if cur:
                cur.close()
            if conn:
                conn.close()
        except:
            pass
