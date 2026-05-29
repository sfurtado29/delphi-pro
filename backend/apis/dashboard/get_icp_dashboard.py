# backend/apis/dashboard/get_icp_dashboard.py
from fastapi import APIRouter, HTTPException, Query
from db import get_conn
import logging

router = APIRouter()

@router.get("/icp")
def get_icp_dashboard(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1)
):
    conn = get_conn()
    cur = conn.cursor(dictionary=True)

    try:
        # Call procedure with all filters NULL
        cur.callproc(
            "Usp_get_icp_filtered_leads",
            (None, None, None, None, None, None, page, page_size)
        )

        results = []
        total = 0

        for i, result in enumerate(cur.stored_results()):
            if i == 0:
                # First result set → total count
                total_row = result.fetchone()
                total = total_row["total"] if total_row else 0
            elif i == 1:
                # Second result set → leads data
                results = result.fetchall()

        # Sort by ICP score (descending)
        results.sort(
            key=lambda x: float(x.get("icp_score", 0) or 0),
            reverse=True
        )

        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "data": results
        }

    except Exception as e:
        logging.error(f"Error fetching ICP dashboard data: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch ICP dashboard data")

    finally:
        cur.close()
        conn.close()