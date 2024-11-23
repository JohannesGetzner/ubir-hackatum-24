from sqlalchemy.orm import DeclarativeBase
from enum import Enum

class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models"""
    pass

class ScenarioStatus(str, Enum):
    RUNNING = "RUNNING"
    FINISHED = "FINISHED"
    CREATED = "CREATED"

class AssignmentStatus(str, Enum):
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
