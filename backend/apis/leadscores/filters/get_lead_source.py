# backend/apis/leadscores/filters/get_lead_source.py
from fastapi import APIRouter, HTTPException
from db import get_conn

router = APIRouter()

@router.get("/lead-sources", tags=["Lead Sources"])
async def get_lead_sources():
    query = """
        SELECT DISTINCT
        LOWER(
          SUBSTRING_INDEX(
            SUBSTRING_INDEX(
              REPLACE(REPLACE(REPLACE(Industry_type_link,'https://',''),'http://',''),'www.',''),
              '/', 1
            ),
          '.', 1)
        ) AS source
        FROM tblleads_masterlist
        WHERE Industry_type_link IS NOT NULL
          AND Industry_type_link != ''
        ORDER BY source
    """
    conn = get_conn()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query)
        rows = cursor.fetchall()

        result = [
            {"id": row["source"], "label": row["source"].capitalize()}
            for row in rows if row["source"]
        ]

        return {"lead_sources": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()
