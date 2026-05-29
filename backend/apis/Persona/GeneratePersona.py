# ./backend/apis/Persona/GeneratePersona.py
import math
from typing import Optional
from fastapi import APIRouter, Query, HTTPException
from db import get_conn

router = APIRouter()

# ================================================================
# SORTING PRIORITY MAPS
# ================================================================
PRIORITY_ORDER = {
    "Very High": 1,
    "High": 2,
    "Medium": 3,
    "Low": 4,
    "Very Low": 5
}

TIER_ORDER = {
    "Tier 1": 1,
    "Tier 2": 2,
    "Tier 3": 3,
    "Tier 4": 4
}

# ================================================================
# BUSINESS LOGIC HELPERS
# ================================================================

def derive_persona(job_level_desc: str, persona_tier: str) -> str:

    level = (job_level_desc or "").strip().lower()
    tier  = (persona_tier or "Tier 4").strip()

    if any(k in level for k in ["cxo","c-suite","chief","ceo","cio","cto","cfo","president"]):
        return "Economic Buyer" if tier in ("Tier 1","Tier 2") else "Technical Buyer"

    if any(k in level for k in ["director","vp","vice president","head"]):
        return "Champion" if tier in ("Tier 1","Tier 2") else "Operational Influencer"

    if "manager" in level:
        return "Evaluator"

    if any(k in level for k in ["senior","lead","principal","architect"]):
        return "Technical Evaluator"

    if any(k in level for k in ["procurement","purchasing","admin"]):
        return "Gatekeeper"

    return "Influencer"


def derive_persona_role(persona: str, persona_tier: str, engagement_score: float) -> str:

    tier = (persona_tier or "Tier 4").strip()

    if persona == "Economic Buyer":
        return "Decision Maker"

    if persona == "Champion" or (tier == "Tier 1" and engagement_score >= 70):
        return "Internal Advocate" if engagement_score >= 75 else "Champion"

    if persona == "Gatekeeper" or tier == "Tier 4":
        return "Blocker"

    if persona in ("Technical Buyer","Technical Evaluator","Evaluator","Operational Influencer"):
        return "Influencer"

    return "Influencer"


def derive_combined_priority(icp_score: float, propensity_score: float, persona_tier: str) -> str:

    tier = (persona_tier or "Tier 4").strip()

    if icp_score >= 50 and propensity_score >= 50 and tier == "Tier 1":
        return "Very High"

    if (icp_score >= 50 or propensity_score >= 60) and tier == "Tier 2":
        return "High"

    if (icp_score >= 40 or propensity_score >= 50) and tier == "Tier 3":
        return "Medium"

    if (icp_score >= 30 or propensity_score >= 30) and tier == "Tier 4":
        return "Low"

    return "Very Low"


def derive_recommended_action(combined_priority: str, persona_role: str, persona: str) -> str:

    if combined_priority == "Very High":

        if persona_role == "Decision Maker":
            return "Fast-track to proposal"

        if persona_role in ("Internal Advocate","Champion"):
            return "Equip with sales enablement"

        return "Accelerate consensus building"

    if combined_priority == "High":

        if persona_role == "Decision Maker":
            return "Personalized executive outreach"

        if persona_role in ("Internal Advocate","Champion"):
            return "Equip with sales enablement"

        if persona in ("Technical Buyer","Technical Evaluator"):
            return "Deep-dive architecture call"

        if persona == "Evaluator":
            return "Technical demo + validation"

        return "Engage and qualify"

    if combined_priority == "Medium":

        if persona_role == "Decision Maker":
            return "Nurture with ROI content"

        if persona_role == "Blocker":
            return "Deprioritize / monitor"

        return "Tactical short-cycle close"

    if persona_role == "Blocker":
        return "Suppress from active outreach"

    return "Deprioritize / monitor"


# ================================================================
# HELPER : run stored procedure
# ================================================================

def call_proc(cursor, proc_name: str, args: list) -> list[dict]:

    cursor.callproc(proc_name, args)

    rows = []

    for result in cursor.stored_results():

        columns = [d[0] for d in result.description]

        for row in result.fetchall():
            rows.append(dict(zip(columns,row)))

    return rows


# ================================================================
# ENDPOINT
# ================================================================

@router.get("/leads")
def get_persona_leads(

    country_id: Optional[int] = Query(None),
    industry_id: Optional[int] = Query(None),
    job_level_id: Optional[int] = Query(None),
    jobfunction_id: Optional[int] = Query(None),
    job_title: Optional[str] = Query(None),
    experience: Optional[str] = Query(None),
    call_engagement_id: Optional[int] = Query(None),
    call_rating_id: Optional[int] = Query(None),
    call_status_id: Optional[int] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),

    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200)

):

    conn=None
    cursor=None

    try:

        conn=get_conn()
        cursor=conn.cursor()

        # --------------------------------------------------------
        # STEP 1 : GET LEADS
        # --------------------------------------------------------

        all_leads=call_proc(
            cursor,
            "Usp_get_persona_filtered_leads",
            [
                country_id,
                industry_id,
                job_level_id,
                jobfunction_id,
                job_title,
                experience,
                call_engagement_id,
                call_rating_id,
                call_status_id,
                start_date,
                end_date
            ]
        )

        total=len(all_leads)
        total_pages=max(1,math.ceil(total/page_size))

        start_idx=(page-1)*page_size
        page_leads=all_leads[start_idx:start_idx+page_size]

        result_rows=[]

        # --------------------------------------------------------
        # STEP 2 : SCORE LEADS
        # --------------------------------------------------------

        for idx,lead in enumerate(page_leads,start=start_idx+1):

            lead_id=lead.get("Lead_id")

            breakdown={}

            try:

                rows=call_proc(cursor,"Usp_get_persona_breakdown",[lead_id])

                if rows:
                    breakdown=rows[0]

            except:
                breakdown={}

            def sf(key,default=0.0):
                return float(breakdown.get(key) or default)

            def si(key,default=0):
                return int(breakdown.get(key) or default)

            final_score=sf("Final_Persona_Score")
            engagement_score=sf("Engagement_Score")
            conversion_score=sf("Conversion_Score")
            velocity_score=sf("Deal_Velocity_Score")
            deal_size_score=sf("Deal_Size_Impact_Score")

            persona_tier=breakdown.get("Persona_Tier","Tier 4")
            business_meaning=breakdown.get("Business_Meaning","")

            icp_score=float(lead.get("total_icp_score") or 0)
            propensity_score=float(lead.get("total_propensity_score") or 0)
            job_level_desc=lead.get("Job_level_desc") or ""

            persona=derive_persona(job_level_desc,persona_tier)

            persona_role=derive_persona_role(
                persona,
                persona_tier,
                engagement_score
            )

            combined_priority=derive_combined_priority(
                icp_score,
                propensity_score,
                persona_tier
            )

            recommended_action=derive_recommended_action(
                combined_priority,
                persona_role,
                persona
            )

            result_rows.append({

                "sr_no":idx,
                "lead_id":lead_id,
                "company_name":lead.get("Company_name") or "",
                "job_title":lead.get("Job_title") or "",
                "job_level_desc":job_level_desc,
                "job_function_desc":lead.get("Jobfunction_desc") or "",
                "country_name":lead.get("Country_name") or "",
                "industry_desc":lead.get("Standard_industry_desc") or "",

                "icp_score":round(icp_score,2),
                "propensity_score":round(propensity_score,2),
                "engagement_score":round(engagement_score,2),
                "conversion_score":round(conversion_score,2),
                "velocity_score":round(velocity_score,2),
                "deal_size_score":round(deal_size_score,2),
                "final_persona_score":round(final_score,2),

                "persona":persona,
                "persona_tier":persona_tier,
                "business_meaning":business_meaning,
                "persona_role":persona_role,
                "combined_priority":combined_priority,
                "recommended_action":recommended_action
            })

        # --------------------------------------------------------
        # STEP 3 : SORT RESULTS
        # --------------------------------------------------------

        result_rows.sort(
            key=lambda x: (
                PRIORITY_ORDER.get(x["combined_priority"],6),
                TIER_ORDER.get(x["persona_tier"],5)
            )
        )

        return {

            "status":"success",
            "total":total,
            "page":page,
            "page_size":page_size,
            "total_pages":total_pages,
            "leads":result_rows

        }

    except Exception as e:

        raise HTTPException(status_code=500,detail=str(e))

    finally:

        if cursor:
            try: cursor.close()
            except: pass

        if conn:
            try: conn.close()
            except: pass