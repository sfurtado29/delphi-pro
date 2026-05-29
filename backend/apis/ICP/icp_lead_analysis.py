# # # backend/apis/ICP/icp_lead_analysis.py
# from fastapi import APIRouter, HTTPException
# from db import get_conn

# router = APIRouter(prefix="/icp", tags=["ICP Analysis"])


# @router.get("/leads/{lead_id}/analysis")
# def get_icp_lead_analysis(lead_id: int):

#     conn = get_conn()
#     cursor = conn.cursor(dictionary=True)

#     # -----------------------------------
#     # 1. Lead Total Scores
#     # -----------------------------------
#     cursor.execute("""
#        SELECT
#                 lm.Lead_id,
#                 lm.Company_name,
#                 CONCAT(lm.First_name,' ',lm.Last_name) AS name,
#                 lm.Email_id,
#                 lm.Phone_number, 
#                 lm.Job_title,
#                 el.Campaign_key_id AS campaign_id,
#                 el.Order_key_id AS order_id,
#                 jl.Job_level_desc,
#                 jf.Jobfunction_desc,
#                 si.Standard_industry_desc AS industry,
#                 es.Employee_size_desc,
#                 rs.Revenue_size_desc,
#                 loc.Location_desc AS country,
                

#                 /* QA STATUS */
#                 COALESCE(qs.QAstatus_desc, 'Not Audited') AS qa_status,
#                 CASE
#                     WHEN qad.Record_id IS NULL THEN 0
#                     ELSE 1
#                 END AS isAudited,

#                 /* SUPPRESSION */
#                 sup.Supressreason_desc,
#                 sup.Supress_until_dt,
#                 sup.Inserted_dt AS suppressed_on_dt

#             FROM tblleads_masterlist lm

#             # LEFT JOIN tblengaged_leads el
#             #     ON el.Lead_id = lm.Lead_id AND el.Isdelete = b'0'
                    
#                 LEFT JOIN (
#                     SELECT e1.*
#                     FROM tblengaged_leads e1
#                     JOIN (
#                         SELECT Lead_id, MAX(Engage_id) AS max_engage_id
#                         FROM tblengaged_leads
#                         WHERE Isdelete = b'0'
#                         AND Isaudited = b'1'
#                         GROUP BY Lead_id
#                     ) e2
#                     ON e1.Lead_id = e2.Lead_id
#                     AND e1.Engage_id = e2.max_engage_id
#                 ) el
#                 ON el.Lead_id = lm.Lead_id


#             LEFT JOIN tblqualityaudit_details qad
#                 ON qad.Engage_id = el.Engage_id AND qad.Isdelete = b'0'

#             LEFT JOIN Mst_tblqualityaudit_status qs
#                 ON qs.QAstatus_id = qad.Auditstatus_id

#             LEFT JOIN Mst_tbljoblevel jl ON jl.Job_level_id = lm.Job_level_id
#             LEFT JOIN Mst_tbljobfunction jf ON jf.Jobfunction_id = lm.Jobfunction_id
#             LEFT JOIN Mst_tblstandardindustry si ON si.Standard_industry_id = lm.Standard_industry_id
#             LEFT JOIN Mst_tblemployeesize es ON es.Employee_size_id = lm.Employee_size_id
#             LEFT JOIN Mst_tblrevenuesize rs ON rs.Revenue_size_id = lm.Revenue_size_id
#             LEFT JOIN Mst_tbllocationelements loc ON loc.Location_id = lm.Country_id

#             LEFT JOIN vw_recent_suppressed_leads sup
#                 ON sup.Lead_id = lm.Lead_id

#             WHERE lm.Lead_id = %s
#             LIMIT 1
#         """, (lead_id,))

#     lead = cursor.fetchone()

#     if not lead:
#         raise HTTPException(status_code=404, detail="Lead not found")

#     # -----------------------------------
#     # 2. Propensity Breakdown (FIXED ✅)
#     # -----------------------------------
#     cursor.execute("""
#         SELECT
#             parameter_name,
#             raw_score,
#             weight,
#             weighted_score
#         FROM vw_lead_score_breakdown
#         WHERE Lead_id = %s
#         ORDER BY weighted_score DESC
#     """, (lead_id,))

#     propensity_breakdown = cursor.fetchall()

#     # -----------------------------------
#     # 3. ICP Breakdown (Already Correct ✅)
#     # -----------------------------------
#     cursor.execute("""
#         SELECT
#             parameter_name,
#             raw_score,
#             weight,
#             weighted_score
#         FROM vw_icp_score_breakdown
#         WHERE Lead_id = %s
#         ORDER BY weighted_score DESC
#     """, (lead_id,))

#     icp_breakdown = cursor.fetchall()

#     cursor.close()
#     conn.close()

#     # -----------------------------------
#     # FINAL RESPONSE
#     # -----------------------------------
#     return {
#         "lead": lead,
#         "breakdown": {
#             "propensity": propensity_breakdown,
#             "icp": icp_breakdown
#         }
#     }


# backend/apis/ICP/icp_lead_analysis.py
from fastapi import APIRouter, HTTPException
from db import get_conn

router = APIRouter(prefix="/icp", tags=["ICP Analysis"])


@router.get("/leads/{lead_id}/analysis")
def get_icp_lead_analysis(lead_id: int):

    conn = get_conn()
    cursor = conn.cursor(dictionary=True)

    # -----------------------------------
    # 1. Lead Full Detail + Total Scores
    # -----------------------------------
    cursor.execute("""
        SELECT
            lm.Lead_id,
            lm.Company_name,
            CONCAT(lm.First_name,' ',lm.Last_name) AS name,
            lm.Email_id,
            lm.Phone_number,
            lm.Job_title,

            el.Campaign_key_id AS campaign_id,
            el.Order_key_id AS order_id,

            jl.Job_level_desc,
            jf.Jobfunction_desc,
            si.Standard_industry_desc AS industry,
            es.Employee_size_desc,
            rs.Revenue_size_desc,
            loc.Location_desc AS country,

            /* TOTAL SCORES */
            pq.total_propensity_score AS propensity_score,
            icp.icp_score,

            /* QA STATUS */
            COALESCE(qs.QAstatus_desc, 'Not Audited') AS qa_status,
            CASE
                WHEN qad.Record_id IS NULL THEN 0
                ELSE 1
            END AS isAudited,

            /* SUPPRESSION */
            sup.Supressreason_desc,
            sup.Supress_until_dt,
            sup.Inserted_dt AS suppressed_on_dt

        FROM tblleads_masterlist lm

        /* Latest audited engaged lead */
        LEFT JOIN (
            SELECT e1.*
            FROM tblengaged_leads e1
            JOIN (
                SELECT Lead_id, MAX(Engage_id) AS max_engage_id
                FROM tblengaged_leads
                WHERE Isdelete = b'0'
                  AND Isaudited = b'1'
                GROUP BY Lead_id
            ) e2
            ON e1.Lead_id = e2.Lead_id
            AND e1.Engage_id = e2.max_engage_id
        ) el
        ON el.Lead_id = lm.Lead_id

        /* QA */
        LEFT JOIN tblqualityaudit_details qad
            ON qad.Engage_id = el.Engage_id
           AND qad.Isdelete = b'0'

        LEFT JOIN Mst_tblqualityaudit_status qs
            ON qs.QAstatus_id = qad.Auditstatus_id

        /* Lookup tables */
        LEFT JOIN Mst_tbljoblevel jl
            ON jl.Job_level_id = lm.Job_level_id

        LEFT JOIN Mst_tbljobfunction jf
            ON jf.Jobfunction_id = lm.Jobfunction_id

        LEFT JOIN Mst_tblstandardindustry si
            ON si.Standard_industry_id = lm.Standard_industry_id

        LEFT JOIN Mst_tblemployeesize es
            ON es.Employee_size_id = lm.Employee_size_id

        LEFT JOIN Mst_tblrevenuesize rs
            ON rs.Revenue_size_id = lm.Revenue_size_id

        LEFT JOIN Mst_tbllocationelements loc
            ON loc.Location_id = lm.Country_id

        /* Suppression */
        LEFT JOIN vw_recent_suppressed_leads sup
            ON sup.Lead_id = lm.Lead_id

        /* Total Propensity Score */
        LEFT JOIN vw_propensity_qualified_leads pq
            ON pq.Lead_id = lm.Lead_id

        /* Total ICP Score */
        LEFT JOIN vw_icp_total_score icp
            ON icp.Lead_id = lm.Lead_id
           AND icp.Campaign_key_id = pq.Campaign_key_id

        WHERE lm.Lead_id = %s
        LIMIT 1
    """, (lead_id,))

    lead = cursor.fetchone()

    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    # -----------------------------------
    # 2. Propensity Breakdown
    # -----------------------------------
    cursor.execute("""
        SELECT
            parameter_name,
            raw_score,
            weight,
            weighted_score
        FROM vw_lead_score_breakdown
        WHERE Lead_id = %s
        ORDER BY weighted_score DESC
    """, (lead_id,))
    propensity_breakdown = cursor.fetchall()

    # -----------------------------------
    # 3. ICP Breakdown
    # -----------------------------------
    cursor.execute("""
        SELECT
            parameter_name,
            raw_score,
            weight,
            weighted_score
        FROM vw_icp_score_breakdown
        WHERE Lead_id = %s
        ORDER BY weighted_score DESC
    """, (lead_id,))
    icp_breakdown = cursor.fetchall()

    cursor.close()
    conn.close()

    # -----------------------------------
    # FINAL RESPONSE (Single API)
    # -----------------------------------
    return {
        "lead": lead,
        "breakdown": {
            "propensity": propensity_breakdown,
            "icp": icp_breakdown
        }
    }
