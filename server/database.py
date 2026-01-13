from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import os

# Check for DATABASE_URL env var (Provided by Render/Heroku)
# Check for DATABASE_URL env var or use specific path for Render Disk
# On Render, we will mount a disk to /var/data
if os.path.exists("/var/data"):
    DB_PATH = "/var/data/users.db"
    SQLALCHEMY_DATABASE_URL = "sqlite:////var/data/users.db"
else:
    DB_PATH = "users.db (Local/Ephemeral)"
    SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./users.db")

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
