#!/bin/sh
set -e

DB_HOST="${DB_HOST:-db}"
DB_PORT="${DB_PORT:-3306}"

echo "Waiting for MySQL at ${DB_HOST}:${DB_PORT}..."
until python - <<'PY'
import os
import pymysql

try:
    conn = pymysql.connect(
        host=os.getenv("DB_HOST", "db"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        connect_timeout=3,
        ssl_disabled=True,
    )
    conn.close()
except Exception:
    raise SystemExit(1)
raise SystemExit(0)
PY
do
  sleep 2
done
echo "MySQL is up."

if [ "${AUTO_MIGRATE:-true}" = "true" ]; then
  echo "Running Alembic migrations..."
  alembic upgrade head
fi

if [ "${AUTO_SEED:-true}" = "true" ]; then
  echo "Seeding demo data..."
  python scripts/seed.py
fi

echo "Starting API..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
