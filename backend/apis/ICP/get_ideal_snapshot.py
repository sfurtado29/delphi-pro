# backend/apis/ICP/get_ideal_snapshot.py
from fastapi import APIRouter
from db import get_conn

router = APIRouter(prefix="/icp", tags=["ICP Snapshot"])

@router.get("/ideal-snapshot")
def get_ideal_snapshot(industry_id: int, brand_id: int, country_id: int):

    conn = get_conn()
    cur = conn.cursor(dictionary=True)

    cur.callproc("Usp_get_icp_ideal_snapshot",
                 [industry_id, brand_id, country_id])

    results = []
    for result in cur.stored_results():
        results.append(result.fetchall()[0])

    cur.close()
    conn.close()

    return {"snapshot": results}
