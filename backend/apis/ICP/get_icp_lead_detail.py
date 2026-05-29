# backend/apis/ICP/get_icp_lead_detail.py
from fastapi import APIRouter, HTTPException
from db import get_conn

router = APIRouter(
    prefix="/icp",
    tags=["ICP Analysis"]
)
@router.get("/leads/{lead_id}/detail")
def get_icp_lead_analysis(lead_id: int):

    conn = get_conn()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            lm.Lead_id,
            lm.Company_name,
            lm.Job_title,

            si.Standard_industry_desc AS industry,
            loc.Location_desc AS country,

            pq.total_propensity_score AS propensity_score,
            icp.icp_score

        FROM vw_propensity_qualified_leads pq

        JOIN vw_icp_total_score icp
            ON icp.Lead_id = pq.Lead_id
           AND icp.Campaign_key_id = pq.Campaign_key_id

        JOIN tblleads_masterlist lm
            ON lm.Lead_id = pq.Lead_id

        LEFT JOIN Mst_tblstandardindustry si
            ON si.Standard_industry_id = lm.Standard_industry_id

        LEFT JOIN Mst_tbllocationelements loc
            ON loc.Location_id = lm.Country_id

        WHERE pq.Lead_id = %s
    """, (lead_id,))

    lead = cursor.fetchone()

    cursor.close()
    conn.close()

    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    return {"lead": lead}
