from fastapi import APIRouter, HTTPException
from app.db import get_connection
from app.schemas.price import PriceRecord

router = APIRouter()

@router.get("/data")
def get_data():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT datetime, open, high, low, close, volume 
            FROM price_data ORDER BY datetime ASC
        """)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        data = [
            {
                "datetime": r[0],
                "open": float(r[1]),
                "high": float(r[2]),
                "low": float(r[3]),
                "close": float(r[4]),
                "volume": r[5],
            }
            for r in rows
        ]
        return {"data": data}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/data")
def add_price_data(record: PriceRecord):
    """Data validation is done by Pydantic, DB errors are caught."""
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO price_data (datetime, open, high, low, close, volume)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (record.datetime, record.open, record.high,
             record.low, record.close, record.volume)
        )
        conn.commit()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database Error: {str(e)}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return {"message": "Record added successfully"}
