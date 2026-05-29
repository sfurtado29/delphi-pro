# apis/Persona/ScoreConfig/persona_config.py
# apis/Persona/ScoreConfig/persona_config.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from db import get_conn

router = APIRouter(prefix="/persona-config", tags=["Persona Configuration"])


class WeightUpdate(BaseModel):
    parameter_id: int
    weight: int


class ValueUpdate(BaseModel):
    persona_value_id: int
    score: int


# master resolver to fetch names
PARAMETER_MASTER_MAP = {
    1: {
        "table": "Mst_tbljoblevel",
        "id_col": "Job_level_id",
        "name_col": "Job_level_desc",
    },
    2: {
        "table": "Mst_tbljobfunction",
        "id_col": "Jobfunction_id",
        "name_col": "Jobfunction_desc",
    },
    3: {
        "table": "Mst_tblqualityaudit_callEngagement",
        "id_col": "CallEngagement_id",
        "name_col": "Call_engagement",
    },
    4: {
        "table": "Mst_tblqualityaudit_callrating",
        "id_col": "QAcallrating_id",
        "name_col": "QAcallrating_desc",
    },
    5: {
        "table": "Mst_tblqualityaudit_callstatus",
        "id_col": "Callstatus_id",
        "name_col": "Call_status",
    },
}


# GET PARAMETERS
@router.get("/parameters")
def get_persona_parameters():
    conn = get_conn()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT
                p.parameter_id,
                p.parameter_code,
                p.parameter_name,
                w.weight
            FROM mst_persona_parameter p
            JOIN mst_persona_weight w
              ON p.parameter_id = w.parameter_id
            WHERE p.is_active = 1
              AND w.is_active = 1
            ORDER BY p.parameter_id
        """)
        return cursor.fetchall()

    finally:
        cursor.close()
        conn.close()


# UPDATE WEIGHTS
@router.post("/weights")
def update_persona_weights(weights: List[WeightUpdate]):

    if sum(w.weight for w in weights) != 100:
        raise HTTPException(400, "Total weight must be 100")

    conn = get_conn()
    cursor = conn.cursor()

    try:
        for w in weights:
            cursor.execute("""
                UPDATE mst_persona_weight
                SET weight = %s
                WHERE parameter_id = %s
            """, (w.weight, w.parameter_id))

        conn.commit()

        return {"message": "Persona weights updated successfully"}

    finally:
        cursor.close()
        conn.close()


# GET VALUES
@router.get("/values/{parameter_id}")
def get_persona_values(parameter_id: int):

    conn = get_conn()
    cursor = conn.cursor(dictionary=True)

    try:

        cursor.execute("""
            SELECT
                persona_value_id,
                master_value_id,
                score
            FROM mst_persona_value
            WHERE parameter_id = %s
            AND is_active = 1
        """, (parameter_id,))

        rows = cursor.fetchall()

        resolver = PARAMETER_MASTER_MAP.get(parameter_id)

        if not resolver:
            return rows

        for r in rows:
            cursor.execute(f"""
                SELECT {resolver['name_col']} AS name
                FROM {resolver['table']}
                WHERE {resolver['id_col']} = %s
            """, (r["master_value_id"],))

            mv = cursor.fetchone()
            r["master_value_name"] = mv["name"] if mv else None

        return rows

    finally:
        cursor.close()
        conn.close()


# UPDATE VALUES
@router.post("/values/{parameter_id}")
def update_persona_values(parameter_id: int, values: List[ValueUpdate]):

    conn = get_conn()
    cursor = conn.cursor()

    try:

        for v in values:
            cursor.execute("""
                UPDATE mst_persona_value
                SET score = %s
                WHERE persona_value_id = %s
                AND is_active = 1
            """, (v.score, v.persona_value_id))

        conn.commit()

        return {"message": "Persona values updated successfully"}

    finally:
        cursor.close()
        conn.close()