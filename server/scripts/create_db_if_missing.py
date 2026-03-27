"""
Create the MySQL database if it does not exist.

Runs a safe "SHOW DATABASES" check and either:
- prints "Database already exists" if present
- or creates the database with utf8mb4 and prints what happened

Usage (from the `server` folder):
  python scripts/create_db_if_missing.py
"""

from __future__ import annotations

import os
import re

import pymysql
from dotenv import load_dotenv


def _load_env() -> dict[str, str]:
    # Ensure `.env` is loaded when running the script from another directory.
    server_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # server/
    dotenv_path = os.path.join(server_root, ".env")
    load_dotenv(dotenv_path)

    required = ["DB_HOST", "DB_PORT", "DB_USER", "DB_PASSWORD", "DB_NAME"]
    missing = [k for k in required if not os.getenv(k)]
    if missing:
        raise RuntimeError(
            "Missing required environment variables for DB creation: "
            + ", ".join(missing)
            + ". Copy server/.env.example to server/.env and fill in values."
        )

    return {k: os.environ[k] for k in required}


def _validate_db_name(db_name: str) -> str:
    # Keep this conservative to avoid accidental SQL injection via environment variables.
    if not re.match(r"^[A-Za-z0-9_]+$", db_name):
        raise ValueError("DB_NAME contains unsupported characters. Use letters/numbers/underscore only.")
    return db_name


def main() -> None:
    env = _load_env()
    host = env["DB_HOST"]
    port = int(env["DB_PORT"])
    user = env["DB_USER"]
    password = env["DB_PASSWORD"]
    db_name = _validate_db_name(env["DB_NAME"])

    # Connect without selecting a database first.
    conn = pymysql.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        autocommit=True,
        cursorclass=pymysql.cursors.Cursor,
    )
    try:
        with conn.cursor() as cur:
            cur.execute("SHOW DATABASES LIKE %s", (db_name,))
            exists = cur.fetchone() is not None

            if exists:
                print("Database already exists")
                return

            cur.execute(
                "CREATE DATABASE `{}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci".format(db_name)
            )
            print(f"Created database: {db_name}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()

