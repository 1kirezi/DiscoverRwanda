#!/bin/sh
set -e

PORT="${PORT:-8000}"

echo "Waiting for database..."
until python - <<'PY'
import os
from sqlalchemy import create_engine, text

db_url = os.getenv("DATABASE_URL", "").strip()

if db_url:
    engine = create_engine(db_url, pool_pre_ping=True)
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    finally:
        engine.dispose()
    raise SystemExit(0)

try:
    import pymysql
    conn = pymysql.connect(
        host=os.getenv("DB_HOST", "db"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        connect_timeout=3,
    )
    conn.close()
except Exception:
    raise SystemExit(1)
raise SystemExit(0)
PY
do
  sleep 2
done
echo "Database is up."

if [ "${AUTO_MIGRATE:-true}" = "true" ]; then
  echo "Running Alembic migrations..."
  alembic upgrade head
fi

if [ "${AUTO_SEED:-true}" = "true" ]; then
  echo "Seeding demo data..."
  python scripts/seed.py
fi

echo "Starting API..."
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT}"
