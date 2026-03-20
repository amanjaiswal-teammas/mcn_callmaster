from fastapi import APIRouter, HTTPException, Query
import mysql.connector
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

# ---- DB CONFIG ----
DB_CONFIG = {
    "host": "192.168.10.6",
    "user": "root",
    "password": "vicidialnow",
    "database": "dialer_db"
}


# ---- Response Model ----
class DummyResponse(BaseModel):
    number: str
    order_id: str
    scenario: str
    timeline: str


# ---- DB Connection ----
def get_connection():
    return mysql.connector.connect(**DB_CONFIG)


# ---- API ----
@router.get("/api/dummy-data", response_model=DummyResponse)
def get_dummy_data(
    number: Optional[str] = Query(None),
    order_id: Optional[str] = Query(None)
):

    if not number and not order_id:
        raise HTTPException(status_code=400, detail="Provide number or order_id")

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        if number:
            query = """
                SELECT number, order_id, scenario, timeline
                FROM dummy_data
                WHERE number = %s
                LIMIT 1
            """
            cursor.execute(query, (number,))
        else:
            query = """
                SELECT number, order_id, scenario, timeline
                FROM dummy_data
                WHERE order_id = %s
                LIMIT 1
            """
            cursor.execute(query, (order_id,))

        result = cursor.fetchone()

        if not result:
            raise HTTPException(status_code=404, detail="Data not found")

        return result

    finally:
        cursor.close()
        conn.close()
