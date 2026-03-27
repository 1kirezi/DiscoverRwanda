from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import QueuePool
from app.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=settings.DEBUG,
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
