from sqlalchemy import Column, Integer, DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import relationship
from app.db.base import Base


class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    checked_in_at = Column(DateTime(timezone=True), server_default=func.now())
    activity_id = Column(Integer, ForeignKey("activities.id"), nullable=True)

    event = relationship("Event", back_populates="attendances")
    student = relationship("User")
    activity = relationship("Activity")

    __table_args__ = (
        UniqueConstraint("event_id", "student_id", name="uq_event_student"),
    )
