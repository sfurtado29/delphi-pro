# backend/apis/ICP/generate_ICP.py
from fastapi import APIRouter, HTTPException
from typing import Optional
from db import get_conn

router = APIRouter(prefix="/icp", tags=["ICP Scoring"])


@router.get("/leads")
def get_icp_leads(
    country_id: Optional[int] = None,
    industry_id: Optional[int] = None,
    employee_size_id: Optional[int] = None,
    revenue_size_id: Optional[int] = None,
    job_level_id: Optional[int] = None,
    job_function_id: Optional[int] = None,
    # lead_type_id: Optional[int] = None,
    # lead_source_domain: Optional[str] = None,
    # qa_status_id: Optional[int] = None,

    page: int = 1,
    page_size: int = 10
):
    try:
        conn = get_conn()
        cursor = conn.cursor(dictionary=True)

        #  EXACT 11 PARAMS IN CORRECT ORDER
        proc_args = [
            country_id,
            industry_id,
            employee_size_id,
            revenue_size_id,
            job_level_id,
            job_function_id,
            #lead_type_id,
            # lead_source_domain,
            # qa_status_id,
            page,
            page_size
        ]

        cursor.callproc("Usp_get_icp_filtered_leads", proc_args)

        # leads = []
        # for result in cursor.stored_results():
        #     leads = result.fetchall()

        # return {
        #     "page": page,
        #     "page_size": page_size,
        #     "leads": leads
        # }

        results = list(cursor.stored_results())

        #  Result Set 1 → total count
        total = results[0].fetchone()["total"]

        # Result Set 2 → paginated leads
        leads = results[1].fetchall()

        return {
            "page": page,
            "page_size": page_size,
            "total": total,          #  Required for pagination
            "leads": leads
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        cursor.close()
        conn.close()
