"""
Database setup for Intelligent API Automation Platform using SQLite and SQLAlchemy.
Manages persistent storage for projects, endpoints, test cases, executions, and pipelines.
"""

import os
from pathlib import Path
import tempfile
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


def get_db_path() -> Path:
    """Returns database path, safely falling back to /tmp on serverless environments."""
    target_dir = Path(__file__).resolve().parent
    # If running on Vercel or target directory is read-only, write to tempdir
    if os.getenv("VERCEL") or not os.access(target_dir, os.W_OK):
        return Path(tempfile.gettempdir()) / "platform.db"
    return target_dir / "platform.db"


DB_PATH = get_db_path()
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH.as_posix()}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}  # Needed for SQLite in multi-threaded FastAPI
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """FastAPI dependency for database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
