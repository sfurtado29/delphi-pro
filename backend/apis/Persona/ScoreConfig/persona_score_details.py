# # apis/Persona/ScoreConfig/persona_score_details.py
# from fastapi import APIRouter, HTTPException
# import re
# from db import get_conn
# import logging

# router = APIRouter(prefix="/persona-score", tags=["Persona Scoring"])

# # resolver map: parameter_code -> lead column
# PARAMETER_RESOLVER = {
#     "JOB_LEVEL": {
#         "source": "lead",
#         "column": "Job_level_id",
#         "master_table": "Mst_tbljoblevel",
#         "master_id_col": "Job_level_id",
#         "master_name_col": "Job_level_desc"
#     },
#     "JOB_FUNCTION": {
#         "source": "lead",
#         "column": "Jobfunction_id",
#         "master_table": "Mst_tbljobfunction",
#         "master_id_col": "Jobfunction_id",
#         "master_name_col": "Jobfunction_desc"
#     },
#     "CALL_ENGAGEMENT": {
#         "source": "engagement",
#         "column": "CallEngagement_id",
#         "master_table": "Mst_tblqualityaudit_callEngagement",
#         "master_id_col": "CallEngagement_id",
#         "master_name_col": "Call_engagement"
#     },
#     "CALL_RATING": {
#         "source": "audit",
#         "column": "QAcallrating_id",
#         "master_table": "Mst_tblqualityaudit_callrating",
#         "master_id_col": "QAcallrating_id",
#         "master_name_col": "QAcallrating_desc"
#     },
#     "CALL_STATUS": {
#         "source": "audit",
#         "column": "Callstatus_id",
#         "master_table": "Mst_tblqualityaudit_callstatus",
#         "master_id_col": "Callstatus_id",
#         "master_name_col": "Call_status"
#     },
#     "EXPERIENCE": {
#     "source": "lead",
#     "column": "Tenurity",
#     "type": "derived"
#     }
    
# }

# @router.get("/{lead_id}")
# def get_persona_score(lead_id: int):
#     conn = None
#     cur = None

#     try:
#         conn = get_conn()
#         cur = conn.cursor(dictionary=True)

#         # lead
#         cur.execute("""
#             SELECT *
#             FROM tblleads_masterlist
#             WHERE Lead_id = %s
#         """, (lead_id,))
#         lead = cur.fetchone()

#         if not lead:
#             raise HTTPException(404, "Lead not found")

#         # latest engagement
#         cur.execute("""
#             SELECT *
#             FROM tblengaged_leads
#             WHERE Lead_id = %s AND Isdelete = 0
#             ORDER BY Engage_id DESC
#             LIMIT 1
#         """, (lead_id,))
#         engagement = cur.fetchone()

#         # latest QA
#         qa = None
#         if engagement:
#             cur.execute("""
#                 SELECT *
#                 FROM tblqualityaudit_details
#                 WHERE Engage_id = %s AND Isdelete = 0
#                 LIMIT 1
#             """, (engagement["Engage_id"],))
#             qa = cur.fetchone()

#         # parameters + weights
#         cur.execute("""
#             SELECT p.parameter_id, p.parameter_code, p.parameter_name, w.weight
#             FROM mst_persona_parameter p
#             JOIN mst_persona_weight w ON p.parameter_id = w.parameter_id
#             WHERE p.is_active = 1 AND w.is_active = 1
#         """)
#         parameters = cur.fetchall()

#         breakdown = []
#         total = 0

#         for p in parameters:
#             code = p["parameter_code"]
#             resolver = PARAMETER_RESOLVER.get(code)

#             raw_score = 0
#             weighted = 0
#             master_value = None

#             if resolver:
#                 source = resolver["source"]

#                 if source == "lead":
#                     master_value_id = lead.get(resolver["column"])
#                 elif source == "engagement" and engagement:
#                     master_value_id = engagement.get(resolver["column"])
#                 elif source == "audit" and qa:
#                     master_value_id = qa.get(resolver["column"])
#                 else:
#                     master_value_id = None

#                 if master_value_id:
#                     cur.execute("""
#                         SELECT score
#                         FROM mst_persona_value
#                         WHERE parameter_id = %s
#                           AND master_value_id = %s
#                           AND is_active = 1
#                     """, (p["parameter_id"], master_value_id))
#                     row = cur.fetchone()
#                     raw_score = row["score"] if row else 0

#                     # master name
#                     cur.execute(f"""
#                         SELECT {resolver['master_name_col']} AS name
#                         FROM {resolver['master_table']}
#                         WHERE {resolver['master_id_col']} = %s
#                     """, (master_value_id,))
#                     mv = cur.fetchone()
#                     master_value = mv["name"] if mv else None

#             weighted = round((raw_score * p["weight"]) / 100, 2)
#             total += weighted

#             breakdown.append({
#                 "parameter_id": p["parameter_id"],
#                 "parameter_code": code,
#                 "parameter_name": p["parameter_name"],
#                 "master_value": master_value,
#                 "raw_score": raw_score,
#                 "weight": p["weight"],
#                 "weighted_score": weighted
#             })

#         return {
#             "lead_id": lead_id,
#             "total_persona_score": round(total, 2),
#             "breakdown": breakdown
#         }

#     except Exception:
#         logging.exception("persona score failed")
#         raise HTTPException(500, "Persona score calculation failed")

#     finally:
#         if cur: cur.close()
#         if conn: conn.close()


# apis/Persona/ScoreConfig/persona_score_details.py

from fastapi import APIRouter, HTTPException
from db import get_conn
import logging

router = APIRouter(prefix="/persona-score", tags=["Persona Scoring"])

# resolver map: parameter_code -> lead column
PARAMETER_RESOLVER = {
    "JOB_LEVEL": {
        "source": "lead",
        "column": "Job_level_id",
        "master_table": "Mst_tbljoblevel",
        "master_id_col": "Job_level_id",
        "master_name_col": "Job_level_desc"
    },
    "JOB_FUNCTION": {
        "source": "lead",
        "column": "Jobfunction_id",
        "master_table": "Mst_tbljobfunction",
        "master_id_col": "Jobfunction_id",
        "master_name_col": "Jobfunction_desc"
    },
    "CALL_ENGAGEMENT": {
        "source": "engagement",
        "column": "CallEngagement_id",
        "master_table": "Mst_tblqualityaudit_callEngagement",
        "master_id_col": "CallEngagement_id",
        "master_name_col": "Call_engagement"
    },
    "CALL_RATING": {
        "source": "audit",
        "column": "QAcallrating_id",
        "master_table": "Mst_tblqualityaudit_callrating",
        "master_id_col": "QAcallrating_id",
        "master_name_col": "QAcallrating_desc"
    },
    "CALL_STATUS": {
        "source": "audit",
        "column": "Callstatus_id",
        "master_table": "Mst_tblqualityaudit_callstatus",
        "master_id_col": "Callstatus_id",
        "master_name_col": "Call_status"
    },
    "EXPERIENCE": {
        "source": "lead",
        "column": "Tenurity",
        "type": "derived"
    }
}

# experience bucket labels for UI
EXPERIENCE_LABELS = {
    1: "0-3 years",
    2: "4-7 years",
    3: "8-12 years",
    4: "13-20 years",
    5: "21+ years"
}


def get_experience_score(conn, lead_id):
    """
    Fetch experience bucket and score from vw_lead_experience_bucket + mst_persona_value
    """
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT e.experience_bucket AS bucket,
               v.score
        FROM vw_lead_experience_bucket e
        LEFT JOIN mst_persona_value v
               ON v.parameter_id = 6
              AND v.master_value_id = e.experience_bucket
              AND v.is_active = 1
        WHERE e.years IS NOT NULL
    """, (lead_id,))
    row = cur.fetchone()
    cur.close()
    if row:
        return row["bucket"], row["score"] or 0
    else:
        return None, 0


@router.get("/{lead_id}")
def get_persona_score(lead_id: int):
    conn = None
    cur = None
    try:
        conn = get_conn()
        cur = conn.cursor(dictionary=True)

        # fetch lead
        cur.execute("""
            SELECT *
            FROM tblleads_masterlist
            WHERE Lead_id = "%s"
        """, (lead_id,))
        lead = cur.fetchone()
        if not lead:
            raise HTTPException(404, "Lead not found")

        # latest engagement
        cur.execute("""
            SELECT *
            FROM tblengaged_leads
            WHERE Lead_id = %s AND Isdelete = 0
            ORDER BY Engage_id DESC
            LIMIT 1
        """, (lead_id,))
        engagement = cur.fetchone()

        # latest QA
        qa = None
        if engagement:
            cur.execute("""
                SELECT *
                FROM tblqualityaudit_details
                WHERE Engage_id = %s AND Isdelete = 0
                LIMIT 1
            """, (engagement["Engage_id"],))
            qa = cur.fetchone()

        # fetch parameters + weights
        cur.execute("""
            SELECT p.parameter_id, p.parameter_code, p.parameter_name, w.weight
            FROM mst_persona_parameter p
            JOIN mst_persona_weight w ON p.parameter_id = w.parameter_id
            WHERE p.is_active = 1 AND w.is_active = 1
        """)
        parameters = cur.fetchall()

        breakdown = []
        total = 0

        for p in parameters:
            code = p["parameter_code"]
            resolver = PARAMETER_RESOLVER.get(code)

            raw_score = 0
            weighted = 0
            master_value = None
            master_value_id = None

            if resolver:
                # -------- EXPERIENCE DERIVED LOGIC --------
                if code == "EXPERIENCE":
                    master_value_id, raw_score = get_experience_score(conn, lead_id)
                    if master_value_id is None:
                        master_value = "No Experience Data"
                    else:
                        master_value = EXPERIENCE_LABELS.get(master_value_id, "Unknown")

                # -------- NORMAL PARAMETERS --------
                else:
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
                        cur.execute("""
                            SELECT score
                            FROM mst_persona_value
                            WHERE parameter_id = %s
                              AND master_value_id = %s
                              AND is_active = 1
                        """, (p["parameter_id"], master_value_id))
                        row = cur.fetchone()
                        raw_score = row["score"] if row else 0

                        # fetch master name
                        cur.execute(f"""
                            SELECT {resolver['master_name_col']} AS name
                            FROM {resolver['master_table']}
                            WHERE {resolver['master_id_col']} = %s
                        """, (master_value_id,))
                        mv = cur.fetchone()
                        master_value = mv["name"] if mv else None

            weighted = round((raw_score * p["weight"]) / 100, 2)
            total += weighted

            breakdown.append({
                "parameter_id": p["parameter_id"],
                "parameter_code": code,
                "parameter_name": p["parameter_name"],
                "master_value": master_value,
                "raw_score": raw_score,
                "weight": p["weight"],
                "weighted_score": weighted
            })

        return {
            "lead_id": lead_id,
            "total_persona_score": round(total, 2),
            "breakdown": breakdown
        }

    except Exception:
        logging.exception("persona score failed")
        raise HTTPException(500, "Persona score calculation failed")

    finally:
        if cur: cur.close()
        if conn: conn.close()