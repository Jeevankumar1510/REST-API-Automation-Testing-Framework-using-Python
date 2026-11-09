"""
Database setup for Intelligent API Automation Platform using SQLite and SQLAlchemy.
Manages persistent storage for projects, endpoints, test cases, executions, and pipelines.
"""

import os
from pathlib import Path
import tempfile
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Database file location (uses /tmp on Vercel to allow write operations)
if os.getenv("VERCEL"):
    DB_PATH = Path(tempfile.gettempdir()) / "platform.db"
else:
    DB_PATH = Path(__file__).resolve().parent / "platform.db"

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

