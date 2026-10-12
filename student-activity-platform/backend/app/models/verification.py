import enum
from sqlalchemy import Column, Integer, Text, DateTime, Enum, ForeignKey, func
from sqlalchemy.orm import relationship
from app.db.base import Base


class VerificationDecision(str, enum.Enum):
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class Verification(Base):
    __tablename__ = "verifications"

    id = Column(Integer, primary_key=True, index=True)
    activity_id = Column(Integer, ForeignKey("activities.id"), nullable=False)
    verifier_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    decision = Column(Enum(VerificationDecision), nullable=False)
    remarks = Column(Text, nullable=True)
    decided_at = Column(DateTime(timezone=True), server_default=func.now())

    activity = relationship("Activity", back_populates="verifications")
    verifier = relationship("User")
