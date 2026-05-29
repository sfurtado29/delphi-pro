# backend/apis/leadscores/filters/get_campaigns.py
from fastapi import APIRouter, HTTPException, Query
from db import get_conn
import logging

router = APIRouter()

@router.get("/campaigns")
def get_campaigns(q: str = Query(None, description="optional substring filter on Order_id or Order_name"),
                  limit: int = Query(1000, description="max rows to return")):
    """
    Returns:
      { "campaigns": [ { "id": <Order_key_id>, "label": "<Order_id> | <Order_name>" }, ... ] }
    Only campaigns which have at least one engaged lead are returned.
    Optional query `q` does case-insensitive substring match against Order_id or Order_name.
    """
    conn = None
    cur = None
    try:
        if limit is None or limit <= 0:
            limit = 1000
        if limit > 5000:
            limit = 5000

        conn = get_conn()
        cur = conn.cursor(dictionary=True)

        if q:
            sql = """
                SELECT DISTINCT 
                       od.Order_key_id AS id,
                       TRIM(od.Order_id) AS order_code,
                       TRIM(od.Order_name) AS order_name
                FROM tblorder_details od
                INNER JOIN tblengaged_leads el 
                    ON el.Order_key_id = od.Order_key_id
                   AND el.Isdelete = b'0'
                WHERE od.Isactive = b'1'
                  AND (LOWER(od.Order_id) LIKE LOWER(%s) 
                       OR LOWER(od.Order_name) LIKE LOWER(%s))
                ORDER BY od.Order_name
                LIMIT %s
            """
            params = (f"%{q}%", f"%{q}%", limit)
        else:
            sql = """
                SELECT DISTINCT 
                       od.Order_key_id AS id,
                       TRIM(od.Order_id) AS order_code,
                       TRIM(od.Order_name) AS order_name
                FROM tblorder_details od
                INNER JOIN tblengaged_leads el 
                    ON el.Order_key_id = od.Order_key_id
                   AND el.Isdelete = b'0'
                WHERE od.Isactive = b'1'
                ORDER BY od.Order_name
                LIMIT %s
            """
            params = (limit,)

        cur.execute(sql, params)
        rows = cur.fetchall() or []

        campaigns = []
        for r in rows:
            code = r.get("order_code") or ""
            name = r.get("order_name") or ""
            if code and name:
                label = f"{code} | {name}"
            else:
                label = code or name or "Unknown Campaign"

            campaigns.append({"id": r["id"], "label": label})

        return {"campaigns": campaigns}

    except Exception as e:
        logging.exception("get_campaigns failed")
        raise HTTPException(status_code=500, detail="Failed to fetch campaigns")
    finally:
        try:
            if cur:
                cur.close()
            if conn:
                conn.close()
        except:
            pass
