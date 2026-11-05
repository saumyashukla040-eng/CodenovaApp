import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Anchor database to project root directory for persistent storage
BASE_DIR = Path(__file__).resolve().parent.parent
DB_FILE = BASE_DIR / "codenova.db"
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_FILE.as_posix()}"

# SQLite requires check_same_thread=False for multithreaded FastAPI requests
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """
    FastAPI dependency that yields an independent database session
    per request and ensures it is properly closed afterwards.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
