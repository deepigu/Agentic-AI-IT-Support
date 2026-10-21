
import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


# ==================================
# DATABASE CONFIGURATION
# ==================================

BASE_DIR = Path(__file__).resolve().parent

SQLITE_PATH = BASE_DIR / "it_support.db"

DEFAULT_DATABASE_URL = (
    f"sqlite:///{SQLITE_PATH.as_posix()}"
)

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    DEFAULT_DATABASE_URL
)

# Support older PostgreSQL URL formats
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace(
        "postgres://",
        "postgresql://",
        1
    )


# ==================================
# CREATE DATABASE ENGINE
# ==================================

if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True
    )


# ==================================
# CREATE DATABASE SESSION
# ==================================

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# ==================================
# BASE CLASS FOR DATABASE MODELS
# ==================================

Base = declarative_base()
