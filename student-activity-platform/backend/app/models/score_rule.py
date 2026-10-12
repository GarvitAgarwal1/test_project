from sqlalchemy import Column, Integer, Boolean, Enum, JSON, func
from app.db.base import Base
from app.models.activity import ActivityCategory


class ScoreRule(Base):
    __tablename__ = "score_rules"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(Enum(ActivityCategory), unique=True, nullable=False)
    base_points = Column(Integer, nullable=False, default=5)
    level_multiplier = Column(JSON, default=lambda: {"college": 1.0, "state": 1.5, "national": 2.0, "international": 3.0})
    position_bonus = Column(JSON, default=lambda: {"winner": 5, "runner-up": 3, "participant": 0})
    active = Column(Boolean, default=True)
