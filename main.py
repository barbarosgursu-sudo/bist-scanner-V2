import os
import psycopg2
from fastapi import FastAPI

app = FastAPI()

def get_db_connection():
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise Exception("DATABASE_URL not found")
    conn = psycopg2.connect(database_url)
    return conn

@app.get("/")
def root():
    return {"message": "BIS_V2 running"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/db-test")
def db_test():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1;")
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return {"db_status": "connected", "result": result}
    except Exception as e:
        return {"db_status": "error", "error": str(e)}

@app.get("/init-intraday-table")
def init_intraday_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS intraday_state (
            symbol VARCHAR(20) PRIMARY KEY,
            trade_date DATE NOT NULL,
            open_price DOUBLE PRECISION NOT NULL,
            dip_detected BOOLEAN NOT NULL DEFAULT FALSE,
            triggered BOOLEAN NOT NULL DEFAULT FALSE,
            first_dip_time TIMESTAMP NULL,
            trigger_time TIMESTAMP NULL,
            last_checked_price DOUBLE PRECISION NULL,
            last_update_time TIMESTAMP NULL
        );
    """)
    conn.commit()
    cursor.close()
    conn.close()
    return {"status": "intraday_state table created"}

@app.get("/state-count")
def state_count():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM intraday_state;")
    count = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return {"count": count}

@app.get("/reset-intraday-state")
def reset_intraday_state():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("TRUNCATE intraday_state;")
    conn.commit()
    cursor.close()
    conn.close()
    return {"status": "intraday_state reset"}
