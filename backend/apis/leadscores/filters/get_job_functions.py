# backend/apis/leadscores/filters/get_job_functions.py
from fastapi import APIRouter, HTTPException
from db import get_conn
import logging

router = APIRouter()

@router.get("/job_functions")
def get_job_functions():
    """
    Returns:
      { "job_functions": [ { "id": <Jobfunction_id>, "label": <Jobfunction_desc> }, ... ] }
    """
    conn = None
    cur = None
    try:
        conn = get_conn()
        cur = conn.cursor(dictionary=True)

        cur.execute("""
            SELECT
              Jobfunction_id AS id,
              Jobfunction_desc AS label
            FROM Mst_tbljobfunction
            WHERE Isactive = b'1'
            ORDER BY Jobfunction_desc;
        """)
        rows = cur.fetchall() or []
        job_functions = [{"id": r["id"], "label": r["label"]} for r in rows]
        return {"job_functions": job_functions}

    except Exception as e:
        logging.exception("get_job_functions failed")
        raise HTTPException(status_code=500, detail="Failed to fetch job functions")
    finally:
        try:
            if cur:
                cur.close()
            if conn:
                conn.close()
        except:
            pass
