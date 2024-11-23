from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from pathlib import Path

# Import all models to ensure they are registered with SQLAlchemy
from models import Base, Scenario, Vehicle, Customer, Assignment

# Create engine
DB_PATH = Path("instance/hackathon.db")
DB_PATH.parent.mkdir(parents=True, exist_ok=True)
engine = create_engine(f"sqlite:///{DB_PATH}", echo=True)

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
