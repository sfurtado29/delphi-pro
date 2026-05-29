# backend/apis/leadscores/scoring/get_lead_score_details.py
from fastapi import APIRouter, HTTPException
from db import get_conn
import logging

router = APIRouter()

@router.get("/lead-score-details/{lead_id}")
def get_lead_score_details(lead_id: int):
    conn = None
    cur = None

    try:
        conn = get_conn()
        cur = conn.cursor(dictionary=True)

        query = """
        SELECT
            p.parameter_code,
            p.parameter_name,
            sv.score AS raw_score,
            w.weight,
            ROUND(sv.score * w.weight / 100, 2) AS weighted_score,

            CASE p.parameter_code
                WHEN 'JOB_LEVEL' THEN jl.Job_level_desc
                WHEN 'JOB_FUNCTION' THEN jf.Jobfunction_desc
                WHEN 'EMP_SIZE' THEN es.Employee_size_desc
                WHEN 'REV_SIZE' THEN rs.Revenue_size_desc
                WHEN 'LEAD_TYPE' THEN lt.Leadtype_desc
                WHEN 'AUDIT_STATUS' THEN ast.Auditstatus_desc
                WHEN 'PRIMARY_REASON' THEN pr.Primaryreason_desc
                WHEN 'CALL_RATING' THEN cr.Callrating_desc
            END AS matched_value

        FROM tblleads_masterlist lm
        JOIN tblengaged_leads el ON el.Lead_id = lm.Lead_id

        JOIN mst_scoring_parameter p ON p.is_active = 1
        JOIN mst_scoring_weight w ON w.parameter_id = p.parameter_id AND w.is_active = 1
        JOIN mst_scoring_value sv ON sv.parameter_id = p.parameter_id AND sv.is_active = 1

        /* MASTER TABLES */
        LEFT JOIN Mst_tbljoblevel jl ON jl.Job_level_id = lm.Job_level_id
        LEFT JOIN Mst_tbljobfunction jf ON jf.Jobfunction_id = lm.Jobfunction_id
        LEFT JOIN Mst_tblemployeesize es ON es.Employee_size_id = lm.Employee_size_id
        LEFT JOIN Mst_tblrevenuesize rs ON rs.Revenue_size_id = lm.Revenue_size_id
        LEFT JOIN Mst_tblleadtype lt ON lt.Leadtype_id = el.Leadtype_id
        LEFT JOIN tblqualityaudit_details qa ON qa.Engage_id = el.Engage_id AND qa.Isdelete = 0
        LEFT JOIN Mst_tblauditstatus ast ON ast.Auditstatus_id = qa.Auditstatus_id
        LEFT JOIN Mst_tblprimaryreason pr ON pr.Primaryreason_id = qa.Primaryreason_id
        LEFT JOIN Mst_tblcallrating cr ON cr.Callrating_id = qa.Callrating_id

        WHERE lm.Lead_id = %s
          AND (
                (p.parameter_code = 'JOB_LEVEL' AND sv.master_value_id = lm.Job_level_id)
             OR (p.parameter_code = 'JOB_FUNCTION' AND sv.master_value_id = lm.Jobfunction_id)
             OR (p.parameter_code = 'EMP_SIZE' AND sv.master_value_id = lm.Employee_size_id)
             OR (p.parameter_code = 'REV_SIZE' AND sv.master_value_id = lm.Revenue_size_id)
             OR (p.parameter_code = 'LEAD_TYPE' AND sv.master_value_id = el.Leadtype_id)
             OR (p.parameter_code = 'AUDIT_STATUS' AND sv.master_value_id = qa.Auditstatus_id)
             OR (p.parameter_code = 'PRIMARY_REASON' AND sv.master_value_id = qa.Primaryreason_id)
             OR (p.parameter_code = 'CALL_RATING' AND sv.master_value_id = qa.Callrating_id)
          )
        ORDER BY weighted_score DESC
        """

        cur.execute(query, (lead_id,))
        rows = cur.fetchall()

        return {"details": rows}

    except Exception as e:
        logging.exception("Score detail fetch failed")
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
