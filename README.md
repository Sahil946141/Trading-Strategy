# Trading-Strategy

A small FastAPI project that stores historical price data in PostgreSQL and exposes endpoints to:
- insert and fetch price records,
- evaluate a Simple Moving Average (SMA) crossover strategy with an automatic optimization loop to find the best short/long SMA pair.

This repo also includes a Jupyter notebook to bulk-insert CSV price data into the database.

## Features
- REST API to add and retrieve price data.
- Pydantic validation for incoming price records.
- SMA crossover strategy endpoint that:
  - calculates short/long SMAs,
  - generates buy/sell signals,
  - optimizes SMA window lengths (searching multiple short/long combinations),
  - returns best parameters and performance summary.
- Unit tests covering validation, endpoints, and SMA logic.
- Dockerfile for containerized deployment.

## Repo layout (important files)
- app/main.py — FastAPI app and router mounting.
- app/routers/data.py — Endpoints for GET /data and POST /data.
- app/routers/strategy.py — Endpoint for GET /strategy/performance.
- app/schemas/price.py — Pydantic model for price records.
- app/db.py — PostgreSQL connection helper (reads credentials from env).
- app/sql/database.sql — SQL for creating the `price_data` table.
- app/data insertion/data_insertion.ipynb — Jupyter notebook for bulk inserting CSV to DB.
- app/tests/test_app.py — Unit tests using FastAPI TestClient and unittest.
- Dockerfile — build image (Python 3.10 slim).

## Requirements
- Python 3.10+ (project used 3.10 in Dockerfile)
- PostgreSQL
- The Python requirements are in `requirements.txt`.

## Environment variables
Create a `.env` file in the project root with your DB credentials (these names are used by app/db.py):

```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=Trading
DB_USER=postgres
DB_PASSWORD=your_password
```

Make sure to keep `.env` out of version control if it contains secrets.

## Database setup
SQL to create the `price_data` table (adapt as needed):

```sql
CREATE TABLE IF NOT EXISTS price_data (
    datetime TIMESTAMP PRIMARY KEY,
    open DECIMAL,
    high DECIMAL,
    low DECIMAL,
    close DECIMAL,
    volume INTEGER
);
```

Run this on your PostgreSQL instance before starting the app (e.g. via psql or a DB client).

Note: The provided `app/sql/database.sql` file contains SQL lines; ensure you create the table before inserting records.

## Running locally (development)
1. Clone the repo and create a virtual environment:
   - python -m venv .venv
   - source .venv/bin/activate (or `.venv\Scripts\activate` on Windows)

2. Install dependencies:
   - pip install -r requirements.txt

3. Configure environment variables (see above `.env`).

4. Create the database table with the SQL shown in "Database setup".

5. Run the app:
   - uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

The app will be available at http://127.0.0.1:8000

## Docker
Build and run (example):

- Build:
  docker build -t trading-strategy:latest .

- Run (make sure to pass env vars or use a docker-compose to provide DB and env):
  docker run -e DB_HOST=... -e DB_PORT=... -e DB_NAME=... -e DB_USER=... -e DB_PASSWORD=... -p 8000:8000 trading-strategy:latest

Consider using docker-compose to run PostgreSQL + app together.

## API Endpoints

- GET /  
  - Returns a simple greeting: {"message": "Hello, World!"}

- GET /test_db  
  - Attempts a DB connection and returns status.

- GET /data  
  - Returns all rows from `price_data` ordered by datetime.
  - Response:
    {
      "data": [
        {"datetime": "...", "open": 123.4, "high": 125.0, "low": 121.0, "close": 124.0, "volume": 1000},
        ...
      ]
    }

- POST /data  
  - Insert one price record.
  - Expected JSON (Pydantic validated by app/schemas/price.py):
    {
      "datetime": "2025-12-13T10:00:00",
      "open": 100.0,
      "high": 101.0,
      "low": 99.0,
      "close": 100.0,
      "volume": 1000
    }
  - Returns 200 with {"message": "Record added successfully"} on success.
  - Validation errors return 422.

- GET /strategy/performance  
  - Runs SMA crossover optimization across a search grid (short SMA range and long SMA range defined in code).
  - Returns JSON with:
    - strategy: name
    - best_short_sma
    - best_long_sma
    - cumulative_return_percent
    - total_buy_signals
    - total_sell_signals
    - buy_dates, sell_dates (lists of dates)

Example curl to add data:
curl -X POST "http://127.0.0.1:8000/data" -H "Content-Type: application/json" -d '{"datetime":"2025-12-13T10:00:00","open":100,"high":101,"low":99,"close":100,"volume":1000}'

## Tests
The repository includes unit tests using unittest and FastAPI's TestClient.

To run tests:
- python -m unittest discover -v

The tests assume either:
- A test database exists and the app can connect, or
- You mock or adapt DB config for CI. The included tests call actual endpoints and expect the DB to be reachable.

## Notebook: Bulk data insertion
- app/data insertion/data_insertion.ipynb demonstrates reading a CSV and inserting to PostgreSQL using SQLAlchemy.
- Update the CSV path and the DATABASE_URL inside the notebook to point at your database before running.

## Notes & Implementation details
- Validation: Pydantic schema in app/schemas/price.py enforces types and volume > 0.
- DB connection: app/db.py uses psycopg2 and reads credentials from environment variables via python-dotenv (load_dotenv()).
- Strategy: app/routers/strategy.py loads close prices from DB into a DataFrame, converts datetime, computes SMAs and signals, evaluates returns, and searches for best short/long SMA pair. Performance is returned as cumulative percent return.
- SQL: ensure `datetime` uniqueness if you insert records with the same timestamp (current schema uses TIMESTAMP PRIMARY KEY).

## Troubleshooting
- "OperationalError: could not connect to server" — check DB host/port, credentials and that PostgreSQL is running and accessible.
- If POST /data returns 500 with DB error — ensure `price_data` table exists and types are compatible.
- If strategy endpoint returns 404 — there is no price data in `price_data`.

## Contributing
Contributions are welcome. Please:
- Open issues for bugs or feature requests.
- Send PRs with tests and clear descriptions.

## License
Specify a license for the repo (e.g., MIT). Add a LICENSE file if desired.


