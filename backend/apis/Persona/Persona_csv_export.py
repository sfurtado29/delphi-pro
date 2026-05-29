# Add this new endpoint to your ./backend/apis/Persona/GeneratePersona.py file

from fastapi.responses import StreamingResponse
import csv
import io

@router.get("/leads/export")
def export_persona_leads_csv(
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
):
    """
    Export all persona leads matching the filters to CSV format.
    No pagination - exports ALL matching records.
    """
    conn = None
    cursor = None

    try:
        conn = get_conn()
        cursor = conn.cursor()

        # Get ALL leads (no pagination)
        all_leads = call_proc(
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

        # Prepare CSV data
        csv_data = []

        for idx, lead in enumerate(all_leads, start=1):
            lead_id = lead.get("Lead_id")
            breakdown = {}

            try:
                rows = call_proc(cursor, "Usp_get_persona_breakdown", [lead_id])
                if rows:
                    breakdown = rows[0]
            except:
                breakdown = {}

            def sf(key, default=0.0):
                return float(breakdown.get(key) or default)

            def si(key, default=0):
                return int(breakdown.get(key) or default)

            final_score = sf("Final_Persona_Score")
            engagement_score = sf("Engagement_Score")
            conversion_score = sf("Conversion_Score")
            velocity_score = sf("Deal_Velocity_Score")
            deal_size_score = sf("Deal_Size_Impact_Score")

            persona_tier = breakdown.get("Persona_Tier", "Tier 4")
            business_meaning = breakdown.get("Business_Meaning", "")

            icp_score = float(lead.get("total_icp_score") or 0)
            propensity_score = float(lead.get("total_propensity_score") or 0)
            job_level_desc = lead.get("Job_level_desc") or ""

            persona = derive_persona(job_level_desc, persona_tier)
            persona_role = derive_persona_role(persona, persona_tier, engagement_score)
            combined_priority = derive_combined_priority(icp_score, propensity_score, persona_tier)
            recommended_action = derive_recommended_action(combined_priority, persona_role, persona)

            csv_data.append({
                "Sr_No": idx,
                "Lead_ID": lead_id,
                "Company_Name": lead.get("Company_name") or "",
                "Country": lead.get("Country_name") or "",
                "Industry": lead.get("Standard_industry_desc") or "",
                "Job_Title": lead.get("Job_title") or "",
                "Job_Level": job_level_desc,
                "Job_Function": lead.get("Jobfunction_desc") or "",
                "Persona": persona,
                "Persona_Tier": persona_tier,
                "Persona_Role": persona_role,
                "ICP_Score": round(icp_score, 2),
                "Propensity_Score": round(propensity_score, 2),
                "Engagement_Score": round(engagement_score, 2),
                "Conversion_Score": round(conversion_score, 2),
                "Velocity_Score": round(velocity_score, 2),
                "Deal_Size_Score": round(deal_size_score, 2),
                "Final_Persona_Score": round(final_score, 2),
                "Combined_Priority": combined_priority,
                "Recommended_Action": recommended_action,
                "Business_Meaning": business_meaning,
            })

        # Sort by priority and tier
        csv_data.sort(
            key=lambda x: (
                PRIORITY_ORDER.get(x["Combined_Priority"], 6),
                TIER_ORDER.get(x["Persona_Tier"], 5)
            )
        )

        # Create CSV in memory
        output = io.StringIO()
        
        if csv_data:
            fieldnames = csv_data[0].keys()
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(csv_data)

        # Get CSV content
        csv_content = output.getvalue()
        output.close()

        # Return as downloadable file
        return StreamingResponse(
            iter([csv_content]),
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=persona_leads_export.csv"
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        if cursor:
            try:
                cursor.close()
            except:
                pass
        if conn:
            try:
                conn.close()
            except:
                pass