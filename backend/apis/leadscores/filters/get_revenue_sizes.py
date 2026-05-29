# backend/apis/leadscores/filters/get_revenue_sizes.py
from fastapi import APIRouter, HTTPException
from db import get_conn
import logging

router = APIRouter()

@router.get("/revenue_sizes")
def get_revenue_sizes():
    """
    Returns:
      { "revenue_sizes": [ { "id": <Revenue_size_id>, "label": <Revenue_size_desc> } ] }
    """
    conn = None
    cur = None
    try:
        conn = get_conn()
        cur = conn.cursor(dictionary=True)

        cur.execute("""
            SELECT
              Revenue_size_id AS id,
              Revenue_size_desc AS label
            FROM Mst_tblrevenuesize
            WHERE Isactive = b'1'
            ORDER BY Revenue_size_desc;
        """)

        rows = cur.fetchall() or []
        revenue_sizes = [{"id": r["id"], "label": r["label"]} for r in rows]

        return {"revenue_sizes": revenue_sizes}

    except Exception as e:
        logging.exception("get_revenue_sizes failed")
        raise HTTPException(status_code=500, detail="Failed to fetch revenue sizes")

    finally:
        try:
            if cur:
                cur.close()
            if conn:
                conn.close()
        except:
            pass
