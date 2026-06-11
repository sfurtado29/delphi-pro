# profile_routes.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from db import get_conn

router = APIRouter(
    prefix="/profile",
    tags=["Profile"]
)

@router.get("/{user_id}")
def get_company_profile(user_id: int):

    try:
        conn = get_conn()
        cursor = conn.cursor(dictionary=True)

        query = """
        SELECT
            company_name,
            specialties,
            brands,
            services,
            industry,
            headquarters,
            website
        FROM delphi_company_profiles
        WHERE user_id = %s
        ORDER BY id DESC
        LIMIT 1
        """

        cursor.execute(query, (user_id,))
        row = cursor.fetchone()

        if not row:
            raise HTTPException(
                status_code=404,
                detail="Profile not found"
            )

        return {
            "success": True,
            "profile": row
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    finally:
        try:
            cursor.close()
            conn.close()
        except:
            pass


class SaveProductsRequest(BaseModel):
    products: list[str]
    company_type: str | None = None


@router.post("/{user_id}/products")
def save_profile_products(user_id: int, payload: SaveProductsRequest):
    """
    Save or update the brands/services field for the user's latest company profile.
    """
    try:
        conn = get_conn()
        cursor = conn.cursor()

        # Build csv string
        csv_val = ", ".join([p.strip() for p in (payload.products or []) if p and p.strip()])

        # Determine target column based on company_type if provided
        col = 'brands'
        if payload.company_type and 'service' in payload.company_type.lower():
            col = 'services'

        # Update the latest profile row for this user
        query = f"""
        UPDATE delphi_company_profiles
        SET {col} = %s
        WHERE id = (
            SELECT id FROM (
                SELECT id FROM delphi_company_profiles
                WHERE user_id = %s
                ORDER BY id DESC
                LIMIT 1
            ) AS t
        )
        """

        cursor.execute(query, (csv_val, user_id))
        conn.commit()

        return {"success": True, "message": "Products saved."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        try:
            cursor.close()
            conn.close()
        except:
            pass