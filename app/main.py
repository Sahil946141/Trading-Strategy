from fastapi import FastAPI
from app.routers import strategy
from app.db import get_connection
from app.routers import data,strategy

app = FastAPI()

@app.get("/")
def start():
    return {"message": "Hello, World!"}
@app.get("/test_db")
def test_db():
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT 1;")
        cur.fetchone()
        cur.close()
        conn.close()
        return {"status": "connected to database"}
    except Exception as e:
        return {"status": "failed", "error": str(e)}
app.include_router(data.router)
app.include_router(strategy.router)
