import ssl
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import QueuePool
from app.config import settings

# SSL context for Aiven
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

engine = create_engine(
    settings.DATABASE_URL.split("?")[0],
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=settings.DEBUG,
    connect_args={"ssl": ssl_context} if settings.DATABASE_URL.startswith("mysql") else {},
)

# Enable MySQL strict mode and UTF-8
@event.listens_for(engine, "connect")
def set_mysql_options(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("SET NAMES utf8mb4")
    cursor.execute("SET CHARACTER SET utf8mb4")
    cursor.execute("SET character_set_connection=utf8mb4")
    cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

Only three things changed from your original:
1. Added `import ssl` and the `ssl_context` block
2. `.split("?")[0]` on the DATABASE_URL to strip the `?ssl-mode=REQUIRED` part
3. Added `connect_args` with the ssl context

Commit this to `server/app/database.py` on GitHub, then set your `DATABASE_URL` on Render to:
```
mysql+pymysql://avnadmin:<NEW_PASSWORD>@mysql-cd6f08-alustudent-758b.j.aivencloud.com:21749/defaultdb
