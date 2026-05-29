# backend/apis/leadscores/filters/get_lead_type.py
from fastapi import APIRouter, HTTPException, Query
from db import get_conn
import logging

router = APIRouter()

@router.get("/lead-types", tags=["Lead Types"])
async def get_lead_types():
    query = "SELECT Leadtype_id, Leadtype_desc FROM Mst_tblleadtypes WHERE Isactive = 1 ORDER BY Leadtype_id"
    conn = get_conn()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query)
        rows = cursor.fetchall()
        result = [{"id": row["Leadtype_id"], "label": row["Leadtype_desc"]} for row in rows]
        return {"lead_types": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()
