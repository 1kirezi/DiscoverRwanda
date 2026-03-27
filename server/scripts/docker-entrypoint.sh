#!/bin/sh
set -e
PORT="${PORT:-8000}"
echo "Waiting for database..."
until python - <<'PY'
import os, ssl, sys
from sqlalchemy import create_engine, text

db_url = os.getenv("DATABASE_URL", "").strip().split("?")[0]
if not db_url:
    sys.exit(1)

ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

engine = create_engine(
    db_url,
    connect_args={"ssl": ssl_context},
    pool_pre_ping=True,
)
try:
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    sys.exit(0)
except Exception as e:
    print(f"DB not ready: {e}")
    sys.exit(1)
finally:
    engine.dispose()
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
