# backend/apis/ICP/ScoreConfig/icp_config.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from db import get_conn

router = APIRouter(
    prefix="/icp-config",
    tags=["ICP Configuration"]
)

# -----------------------------
# Request Models
# -----------------------------

class WeightUpdate(BaseModel):
    parameter_id: int
    weight: int

class ValueUpdate(BaseModel):
    icp_value_id: int
    score: int

# -----------------------------
# Parameter → Master Table Map
# -----------------------------

ICP_PARAMETER_MASTER_MAP = {
    "JOB_LEVEL": ("Mst_tbljoblevel", "Job_level_id", "Job_level_desc"),
    "JOB_FUNCTION": ("Mst_tbljobfunction", "Jobfunction_id", "Jobfunction_desc"),
    "EMP_SIZE": ("Mst_tblemployeesize", "Employee_size_id", "Employee_size_desc"),
    "REV_SIZE": ("Mst_tblrevenuesize", "Revenue_size_id", "Revenue_size_desc"),
    "LEAD_TYPE": ("Mst_tblleadtypes", "Leadtype_id", "Leadtype_desc"),
    "AUDIT_STATUS": ("Mst_tblqualityaudit_status", "QAstatus_id", "QAstatus_desc"),
    "PRIMARY_REASON": ("Mst_tblqualityaudit_primary_reason", "QAprimaryreason_id", "QAprimaryreason_desc"),
    "CALL_RATING": ("Mst_tblqualityaudit_callrating", "QAcallrating_id", "QAcallrating_desc"),
}

# -----------------------------
# Get ICP Parameters + Weights
# -----------------------------

@router.get("/parameters")
def get_icp_parameters():
    conn = get_conn()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                p.parameter_id,
                p.parameter_name,
                p.parameter_code,
                w.weight
            FROM mst_icp_parameter p
            JOIN mst_icp_weight w
              ON p.parameter_id = w.parameter_id
            WHERE p.is_active = 1
              AND w.is_active = 1
            ORDER BY p.parameter_id
        """)
        return cursor.fetchall()

    finally:
        cursor.close()
        conn.close()

# -----------------------------
# Update ICP Weights
# -----------------------------

@router.post("/weights")
def update_icp_weights(weights: List[WeightUpdate]):
    if sum(w.weight for w in weights) != 100:
        raise HTTPException(400, "Total weight must be 100")

    conn = get_conn()
    cursor = conn.cursor()

    try:
        for w in weights:
            cursor.execute("""
                UPDATE mst_icp_weight
                SET weight = %s
                WHERE parameter_id = %s
            """, (w.weight, w.parameter_id))

        conn.commit()
        return {"message": "ICP weights updated successfully"}

    finally:
        cursor.close()
        conn.close()


# -----------------------------
# Get ICP Values for Parameter
# -----------------------------

@router.get("/values/{parameter_id}")
def get_icp_values(parameter_id: int):
    conn = get_conn()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT parameter_code
            FROM mst_icp_parameter
            WHERE parameter_id = %s
              AND is_active = 1
        """, (parameter_id,))
        row = cursor.fetchone()

        if not row:
            raise HTTPException(status_code=404, detail="Invalid parameter")

        parameter_code = row["parameter_code"]

        if parameter_code not in ICP_PARAMETER_MASTER_MAP:
            raise HTTPException(status_code=400, detail="Unsupported parameter")

        table, id_col, name_col = ICP_PARAMETER_MASTER_MAP[parameter_code]

        query = f"""
            SELECT
                v.icp_value_id AS icp_value_id,
                v.master_value_id,
                m.{name_col} AS master_value_name,
                v.score
            FROM mst_icp_value v
            JOIN {table} m
              ON v.master_value_id = m.{id_col}
            WHERE v.parameter_id = %s
              AND v.is_active = 1
              AND m.Isactive = 1
             ORDER BY m.{name_col}
        """

        cursor.execute(query, (parameter_id,))
        return cursor.fetchall()

    finally:
        cursor.close()
        conn.close()

# -----------------------------
# Update ICP Values
# -----------------------------

# @router.post("/values/{parameter_id}")
# def update_icp_values(parameter_id: int, values: List[ValueUpdate]):
#     conn = get_conn()
#     cursor = conn.cursor()

#     try:
#         for v in values:
#             cursor.execute("""
#                 UPDATE mst_icp_value
#                 SET score = %s
#                 WHERE icp_value_id = %s
#                   AND parameter_id = %s
#                   AND is_active = b'1'
#             """, (v.score, v.icp_value_id, parameter_id))

#             if cursor.rowcount == 0:
#                 raise HTTPException(
#                     status_code=404,
#                     detail=f"Invalid scoring_value_id {v.scoring_value_id}"
#                 )

#         conn.commit()
#         return {"message": "ICP scores updated successfully"}

#     finally:
#         cursor.close()
#         conn.close()



# @router.post("/values/{parameter_id}")
# def update_icp_values(parameter_id: int, values: List[ValueUpdate]):

#     print("PARAMETER:", parameter_id)
#     print("VALUES RECEIVED:", values)

#     conn = get_conn()
#     cursor = conn.cursor()

#     try:
#         for v in values:
#             cursor.execute("""
#                 UPDATE mst_icp_value
#                 SET score = %s
#                 WHERE icp_value_id = %s
#                   AND parameter_id = %s
#                   AND is_active = 1
#             """, (v.score, v.icp_value_id, parameter_id))

#             if cursor.rowcount == 0:
#                 raise HTTPException(
#                     status_code=404,
#                     detail=f"Invalid icp_value_id {v.icp_value_id}"
#                 )

#         conn.commit()
#         return {"message": "ICP scores updated successfully"}

#     finally:
#         cursor.close()
#         conn.close()

@router.post("/values/{parameter_id}")
def update_icp_values(parameter_id: int, values: List[ValueUpdate]):

    conn = get_conn()
    cursor = conn.cursor()

    try:
        for v in values:
            cursor.execute("""
                UPDATE mst_icp_value
                SET score = %s
                WHERE icp_value_id = %s
                  AND parameter_id = %s
            """, (v.score, v.icp_value_id, parameter_id))

        conn.commit()
        return {"message": "ICP scores updated successfully"}

    finally:
        cursor.close()
        conn.close()

