# backend/apis/leadscores/scoring/scoring_config.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from db import get_conn
router = APIRouter(prefix="/scoring-config", tags=["Scoring Configuration"])
class WeightUpdate(BaseModel):
    parameter_id: int
    weight: int
PARAMETER_TABLE_MAP = {
    "JOB_LEVEL": ("Mst_tbljoblevel", "Job_level_id", "Job_level_desc"),
    "JOB_FUNCTION": ("Mst_tbljobfunction", "Jobfunction_id", "Jobfunction_desc"),
    "EMP_SIZE": ("Mst_tblemployeesize", "Employee_size_id", "Employee_size_desc"),
    "REV_SIZE": ("Mst_tblrevenuesize", "Revenue_size_id", "Revenue_size_desc"),
    "LEAD_TYPE": ("Mst_tblleadtypes", "Leadtype_id", "Leadtype_desc"),
    "AUDIT_STATUS": ("Mst_tblqualityaudit_status", "QAstatus_id", "QAstatus_desc"),
    "PRIMARY_REASON": ("Mst_tblqualityaudit_primary_reason", "QAprimaryreason_id", "QAprimaryreason_desc"),
    "CALL_RATING": ("Mst_tblqualityaudit_callrating", "QAcallrating_id", "QAcallrating_desc"),
}
@router.get("/parameters")
def get_parameters():
    conn = get_conn()
    cursor = conn.cursor(dictionary=True)
    try:
        query = """
            SELECT p.parameter_id, p.parameter_name, p.parameter_code, w.weight
            FROM mst_scoring_parameter p
            JOIN mst_scoring_weight w ON p.parameter_id = w.parameter_id
            WHERE p.Is_active = 1 AND w.Is_active = 1
            ORDER BY p.parameter_id
        """
        cursor.execute(query)
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


@router.post("/weights")
def update_weights(weights: List[WeightUpdate]):
    if sum(w.weight for w in weights) != 100:
        raise HTTPException(status_code=400, detail="Total weight must be 100")

    conn = get_conn()
    cursor = conn.cursor()
    try:
        for w in weights:
            cursor.execute("""
                UPDATE mst_scoring_weight
                SET weight = %s
                WHERE parameter_id = %s
            """, (w.weight, w.parameter_id))
        conn.commit()
        return {"message": "Weights updated successfully"}
    finally:
        cursor.close()
        conn.close()


@router.get("/values/{parameter_id}")
def get_scoring_values(parameter_id: int):
    conn = get_conn()
    cursor = conn.cursor(dictionary=True)

    try:
        # Get parameter code
        cursor.execute("""
            SELECT parameter_code
            FROM mst_scoring_parameter
            WHERE parameter_id = %s
              AND is_active = 1
        """, (parameter_id,))
        row = cursor.fetchone()

        if not row:
            raise HTTPException(404, "Invalid parameter")

        parameter_code = row["parameter_code"]

        if parameter_code not in PARAMETER_TABLE_MAP:
            raise HTTPException(400, "Unsupported parameter")

        table, id_col, name_col = PARAMETER_TABLE_MAP[parameter_code]

        query = f"""
            SELECT 
                sv.scoring_value_id,
                sv.master_value_id,
                m.{name_col} AS master_value_name,
                sv.score
            FROM mst_scoring_value sv
            JOIN {table} m
                ON sv.master_value_id = m.{id_col}
            WHERE sv.parameter_id = %s
              AND sv.Is_active = 1
              AND m.Isactive = 1
            ORDER BY m.{name_col}
        """

        cursor.execute(query, (parameter_id,))
        return cursor.fetchall()

    finally:
        cursor.close()
        conn.close()


@router.post("/values/{parameter_id}")
def update_scoring_values(parameter_id: int, values: List[dict]):
    conn = get_conn()
    cursor = conn.cursor()
    try:
        for v in values:
            cursor.execute("""
                UPDATE mst_scoring_value
                SET score = %s
                WHERE scoring_value_id = %s
            """, (v["score"], v["scoring_value_id"]))

        conn.commit()
        return {"message": "Scoring values updated"}
    finally:
        cursor.close()
        conn.close()
