# backend/apis/ICP/ScoreConfig/icp_score_details.py
from fastapi import APIRouter, HTTPException
from db import get_conn
import logging

router = APIRouter(
    prefix="/icp-score",
    tags=["ICP Scoring"]
)

# ---------------------------------------------------
# Parameter → Lead / Engagement column resolver
# ---------------------------------------------------
PARAMETER_VALUE_RESOLVER = {
    "JOB_LEVEL": {
        "source": "lead",
        "column": "Job_level_id",
        "master_name_col": "Job_level_desc",
        "master_table": "Mst_tbljoblevel",
        "master_id_col": "Job_level_id"
    },
    "JOB_FUNCTION": {
        "source": "lead",
        "column": "Jobfunction_id",
        "master_name_col": "Jobfunction_desc",
        "master_table": "Mst_tbljobfunction",
        "master_id_col": "Jobfunction_id"
    },
    "EMP_SIZE": {
        "source": "lead",
        "column": "Employee_size_id",
        "master_name_col": "Employee_size_desc",
        "master_table": "Mst_tblemployeesize",
        "master_id_col": "Employee_size_id"
    },
    "REV_SIZE": {
        "source": "lead",
        "column": "Revenue_size_id",
        "master_name_col": "Revenue_size_desc",
        "master_table": "Mst_tblrevenuesize",
        "master_id_col": "Revenue_size_id"
    },
    "LEAD_TYPE": {
        "source": "engagement",
        "column": "Leadtype_id",
        "master_name_col": "Leadtype_desc",
        "master_table": "Mst_tblleadtypes",
        "master_id_col": "Leadtype_id"
    },
    "AUDIT_STATUS": {
        "source": "audit",
        "column": "Auditstatus_id",
        "master_name_col": "Auditstatus_desc",
        "master_table": "Mst_tblauditstatus",
        "master_id_col": "Auditstatus_id"
    },
    "PRIMARY_REASON": {
        "source": "audit",
        "column": "Primaryreason_id",
        "master_name_col": "Primaryreason_desc",
        "master_table": "Mst_tblprimaryreason",
        "master_id_col": "Primaryreason_id"
    },
    "CALL_RATING": {
        "source": "audit",
        "column": "Callrating_id",
        "master_name_col": "Callrating_desc",
        "master_table": "Mst_tblcallrating",
        "master_id_col": "Callrating_id"
    }
}

# ---------------------------------------------------
# GET ICP SCORE DETAILS FOR A LEAD
# ---------------------------------------------------
@router.get("/{lead_id}")
def get_icp_score_details(lead_id: int):
    conn = None
    cur = None

    try:
        conn = get_conn()
        cur = conn.cursor(dictionary=True)

        # ---------------------------------------------------
        # 1. Fetch Lead base data
        # ---------------------------------------------------
        cur.execute("""
            SELECT *
            FROM tblleads_masterlist
            WHERE Lead_id = %s
        """, (lead_id,))
        lead = cur.fetchone()

        if not lead:
            raise HTTPException(404, "Lead not found")

        # ---------------------------------------------------
        # 2. Fetch latest engagement
        # ---------------------------------------------------
        cur.execute("""
            SELECT *
            FROM tblengaged_leads
            WHERE Lead_id = %s
              AND Isdelete = 0
            ORDER BY Engage_id DESC
            LIMIT 1
        """, (lead_id,))
        engagement = cur.fetchone()

        # ---------------------------------------------------
        # 3. Fetch QA details (if any)
        # ---------------------------------------------------
        qa = None
        if engagement:
            cur.execute("""
                SELECT *
                FROM tblqualityaudit_details
                WHERE Engage_id = %s
                  AND Isdelete = 0
                LIMIT 1
            """, (engagement["Engage_id"],))
            qa = cur.fetchone()

        # ---------------------------------------------------
        # 4. Fetch ICP parameters & weights
        # ---------------------------------------------------
        cur.execute("""
            SELECT
                p.parameter_id,
                p.parameter_code,
                p.parameter_name,
                w.weight
            FROM mst_icp_parameter p
            JOIN mst_icp_weight w
              ON p.parameter_id = w.parameter_id
            WHERE p.is_active = 1
              AND w.is_active = 1
        """)
        parameters = cur.fetchall()

        breakdown = []
        total_score = 0

        # ---------------------------------------------------
        # 5. Calculate score per parameter
        # ---------------------------------------------------
        for p in parameters:
            code = p["parameter_code"]
            resolver = PARAMETER_VALUE_RESOLVER.get(code)

            raw_score = 0
            weighted_score = 0
            master_value_name = None

            if resolver:
                source = resolver["source"]

                if source == "lead":
                    master_value_id = lead.get(resolver["column"])
                elif source == "engagement" and engagement:
                    master_value_id = engagement.get(resolver["column"])
                elif source == "audit" and qa:
                    master_value_id = qa.get(resolver["column"])
                else:
                    master_value_id = None

                if master_value_id:
                    # Fetch raw ICP score
                    cur.execute("""
                        SELECT score
                        FROM mst_icp_value
                        WHERE parameter_id = %s
                          AND master_value_id = %s
                          AND is_active = 1
                    """, (p["parameter_id"], master_value_id))
                    sv = cur.fetchone()

                    raw_score = sv["score"] if sv else 0

                    # Fetch master value name
                    cur.execute(f"""
                        SELECT {resolver['master_name_col']} AS name
                        FROM {resolver['master_table']}
                        WHERE {resolver['master_id_col']} = %s
                    """, (master_value_id,))
                    mv = cur.fetchone()
                    master_value_name = mv["name"] if mv else None

            weighted_score = round((raw_score * p["weight"]) / 100, 2)
            total_score += weighted_score

            breakdown.append({
                "parameter_id": p["parameter_id"],
                "parameter_code": code,
                "parameter_name": p["parameter_name"],
                "master_value": master_value_name,
                "raw_score": raw_score,
                "weight": p["weight"],
                "weighted_score": weighted_score
            })

        return {
            "lead_id": lead_id,
            "total_icp_score": round(total_score, 2),
            "breakdown": breakdown
        }

    except Exception as e:
        logging.exception("ICP score calculation failed")
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
