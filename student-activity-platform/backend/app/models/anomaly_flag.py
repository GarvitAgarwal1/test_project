import enum
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, ForeignKey, func
from sqlalchemy.orm import relationship
from app.db.base import Base


class AnomalySeverity(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"


class AnomalyFlag(Base):
    __tablename__ = "anomaly_flags"

    id = Column(Integer, primary_key=True, index=True)
    activity_id = Column(Integer, ForeignKey("activities.id"), nullable=False)
    rule_code = Column(String(50), nullable=False)
    severity = Column(Enum(AnomalySeverity), nullable=False)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    activity = relationship("Activity", back_populates="anomaly_flags")
