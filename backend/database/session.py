from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
import os

# Import all models to ensure they are registered with SQLAlchemy
from models import Base, Scenario, Vehicle, Customer, Assignment

# Get database URL from environment variable with a default fallback
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://hackatum:hackatum2024@localhost:5433/hackatum')

# Create engine
engine = create_engine(DATABASE_URL, echo=False)

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
