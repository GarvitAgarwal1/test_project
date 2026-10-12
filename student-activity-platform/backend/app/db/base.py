from sqlalchemy.orm import declarative_base

Base = declarative_base()

# Import all models here so that Base.metadata contains all tables for Alembic
# This must be done after Base is defined
def import_models():
    """Import all models to register them with SQLAlchemy."""
    from app.models import (  # noqa: F401
        User, Department, Activity, Verification, OCRResult,
        AnomalyFlag, Event, Attendance, ScoreRule, AuditLog, Portfolio,
    )
