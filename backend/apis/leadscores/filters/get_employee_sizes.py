# backend/apis/leadscores/filters/get_employee_sizes.py
from fastapi import APIRouter, HTTPException
from db import get_conn
import logging

router = APIRouter()

@router.get("/employee_sizes")
def get_employee_sizes():
    """
    Returns:
      { "employee_sizes": [ { "id": <Employee_size_id>, "label": <Employee_size_desc> }, ... ] }
    """
    conn = None
    cur = None
    try:
        conn = get_conn()
        cur = conn.cursor(dictionary=True)

        cur.execute("""
            SELECT
              Employee_size_id AS id,
              Employee_size_desc AS label
            FROM Mst_tblemployeesize
            WHERE Isactive = b'1'
            ORDER BY Employee_size_desc;
        """)
        rows = cur.fetchall() or []
        employee_sizes = [{"id": r["id"], "label": r["label"]} for r in rows]
        return {"employee_sizes": employee_sizes}

    except Exception as e:
        logging.exception("get_employee_sizes failed")
        raise HTTPException(status_code=500, detail="Failed to fetch employee sizes")
    finally:
        try:
            if cur:
                cur.close()
            if conn:
                conn.close()
        except:
            pass
