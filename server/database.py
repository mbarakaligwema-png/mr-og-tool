from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import os

# Check for DATABASE_URL env var (Provided by Render/Heroku)
# Prioritize DATABASE_URL (Postgres) if it exists
if os.getenv("DATABASE_URL"):
    SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")
    DB_PATH = "PostgreSQL (Env Var)"
    print(f"--- DATABASE: Using PostgreSQL from ENV ---")
# Fallback to Render Disk if no DATABASE_URL
elif os.path.exists("/var/data"):
    DB_PATH = "/var/data/users.db"
    SQLALCHEMY_DATABASE_URL = "sqlite:////var/data/users.db"
    print(f"--- DATABASE: Using Render Persistent Disk ({DB_PATH}) ---")
# Fallback to Ephemeral Local SQLite
else:
    DB_PATH = "users.db (Local/Ephemeral)"
    SQLALCHEMY_DATABASE_URL = "sqlite:///./users.db"
    print(f"--- DATABASE: Using Ephemeral Local SQLite ({DB_PATH}) ---")

# Fix for Render using 'postgres://' instead of 'postgresql://'
if SQLALCHEMY_DATABASE_URL and SQLALCHEMY_DATABASE_URL.startswith("postgres://"):
    SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("postgres://", "postgresql://", 1)

connect_args = {}
if "sqlite" in SQLALCHEMY_DATABASE_URL:
    connect_args = {"check_same_thread": False}

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args=connect_args
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
