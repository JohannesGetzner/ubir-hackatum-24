from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from pathlib import Path
import os

# Import all models to ensure they are registered with SQLAlchemy
from models import Base, Scenario, Vehicle, Customer, Assignment

# Create engine
DB_PATH = Path("instance/hackathon.db")
DB_DIR = DB_PATH.parent
DB_DIR.mkdir(parents=True, exist_ok=True)

# Ensure the directory has the right permissions
os.chmod(DB_DIR, 0o777)

engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db() -> None:
    """Initialize the database by creating all tables."""
    Base.metadata.create_all(bind=engine)

def get_db() -> Session:
    """Get a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
