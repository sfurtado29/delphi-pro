# backend/apis/leadscores/filters/get_job_levels.py
from fastapi import APIRouter, HTTPException
from db import get_conn
import logging

router = APIRouter()

@router.get("/job_levels")
def get_job_levels():
    """
    Returns:
      { "job_levels": [ { "id": <Job_level_id>, "label": <Job_level_desc> }, ... ] }
    """
    conn = None
    cur = None
    try:
        conn = get_conn()
        cur = conn.cursor(dictionary=True)

        cur.execute("""
            SELECT
              Job_level_id AS id,
              Job_level_desc AS label
            FROM Mst_tbljoblevel
            WHERE Isactive = b'1'
            ORDER BY Job_level_desc;
        """)
        rows = cur.fetchall() or []
        job_levels = [{"id": r["id"], "label": r["label"]} for r in rows]
        return {"job_levels": job_levels}

    except Exception as e:
        logging.exception("get_job_levels failed")
        raise HTTPException(status_code=500, detail="Failed to fetch job levels")
    finally:
        try:
            if cur:
                cur.close()
            if conn:
                conn.close()
        except:
            pass
