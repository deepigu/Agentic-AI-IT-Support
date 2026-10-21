
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


# ==================================
# DATABASE FILE LOCATION
# ==================================

BASE_DIR = Path(__file__).resolve().parent

DATABASE_PATH = BASE_DIR / "it_support.db"

DATABASE_URL = f"sqlite:///{DATABASE_PATH.as_posix()}"


# ==================================
# CREATE DATABASE ENGINE
# ==================================

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
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
