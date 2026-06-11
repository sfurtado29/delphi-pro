# campaign_cortex_service.py
# ─────────────────────────────────────────────────────────────
# Queries Snowflake Cortex using the CAMPAIGN_SUGGESTION semantic
# model. Underlying view: delphi_db.public.vw_campaign_targeting_context
#
# IMPORTANT: geography and industry values are passed verbatim
# from the user — no normalisation. The DB stores "Banking" not
# "Finance", "Afghanistan" not an abbreviation. Any mapping
# before this point loses data.
# ─────────────────────────────────────────────────────────────

from __future__ import annotations
from ..context_engine.cortex_service import query_cortex_analyst
import logging

logger = logging.getLogger(__name__)
from db import get_conn
from mysql.connector import Error


def find_similar_campaigns(
    geography: str,
    industry: str,
    limit: int = 5,
) -> list[dict]:
    """
    Find past campaigns matching geography + industry.
    Values are passed exactly as received — Cortex handles matching
    against the exact strings stored in vw_campaign_targeting_context.
    """
    prompt = (
        f"Show past campaigns where target_industry is '{industry}' "
        f"and target_geography is '{geography}'. "
        f"Include client_name, campaign_information, campaign_code, "
        f"insertion_order_number, target_employee_size, target_revenue_size, "
        f"and effective_total_quantity. "
        f"Limit {limit}."
    )
    return query_cortex_analyst(prompt, model="campaign")


def get_campaign_icp_details(campaign_code: str) -> list[dict]:
    """
    Fetch ICP targeting breakdown for a specific campaign by campaign_code.
    """
    prompt = (
        f"Show the targeting details for campaign_code '{campaign_code}'. "
        f"Include target_job_function, target_job_level, target_employee_size, "
        f"target_revenue_size, target_geography, and total engaged leads."
    )
    return query_cortex_analyst(prompt, model="campaign")


def get_icp_leads(geography: str, industry: str, limit: int = 50) -> list[dict]:
    """
    Fetch lead records that match the ICP derived from geography + industry.
    Returns a list of prospect dicts suitable for frontend consumption.
    """
    prompt = (
        f"Return up to {limit} prospect records matching target_industry '{industry}' "
        f"and target_geography '{geography}'. Include fields: company_name, industry, "
        f"hq_location, employees, title, contact_name, email, phone, icp_fit, propensity_score."
    )
    try:
        results = query_cortex_analyst(prompt, model="campaign")
        logger.info("get_icp_leads: fetched %d records for %s / %s", len(results or []), geography, industry)
        return results
    except Exception as e:
        logger.exception("get_icp_leads: Cortex query failed for %s / %s: %s", geography, industry, e)
        return []


def get_icp_leads_db(geography: str, industry: str, limit: int = 50) -> list[dict]:
    """
    Fast direct DB lookup for prospects matching geography+industry using
    the MySQL connection pool (if configured). Returns a list of dicts
    compatible with the frontend leads table.
    """
    try:
        conn = get_conn()
        cur = conn.cursor(dictionary=True)

        # Try a few candidate tables/views in order. Adapt as necessary
        queries = [
            ("SELECT company_name, industry, hq_location, employees, title, contact_name, email, phone, icp_fit, propensity_score FROM delphi_leads WHERE industry = %s AND hq_location = %s LIMIT %s", (industry, geography, limit)),
            ("SELECT company_name, industry, country AS hq_location, employees, title, contact_name, email, phone, icp_fit, propensity_score FROM leads WHERE industry = %s AND country = %s LIMIT %s", (industry, geography, limit)),
            ("SELECT campaign_information as company_name, target_industry as industry, target_geography as hq_location, target_employee_size as employees, '' as title, '' as contact_name, '' as email, '' as phone, '' as icp_fit, 0 as propensity_score FROM vw_campaign_targeting_context WHERE target_industry = %s AND target_geography = %s LIMIT %s", (industry, geography, limit)),
        ]

        for sql, params in queries:
            try:
                cur.execute(sql, params)
                rows = cur.fetchall()
                if rows:
                    out = []
                    for r in rows:
                        out.append({
                            "company": r.get("company_name") or r.get("campaign_information") or "",
                            "industry": r.get("industry") or "",
                            "hq_location": r.get("hq_location") or "",
                            "employees": r.get("employees") or "",
                            "title": r.get("title") or "",
                            "contact": r.get("contact_name") or "",
                            "email": r.get("email") or "",
                            "phone": r.get("phone") or "",
                            "icp_fit": r.get("icp_fit") or "",
                            "propensity": r.get("propensity_score") or 0,
                        })
                    logger.info("get_icp_leads_db: found %d rows using query", len(out))
                    return out
            except Error:
                # try next query
                continue

        return []
    except Exception as e:
        logger.exception("get_icp_leads_db: DB query failed: %s", e)
        return []
    finally:
        try:
            cur.close()
            conn.close()
        except Exception:
            pass