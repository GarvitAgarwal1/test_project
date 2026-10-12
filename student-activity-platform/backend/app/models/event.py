from sqlalchemy import Column, Integer, String, Text, Date, DateTime, Boolean, Enum, ForeignKey, func
from sqlalchemy.orm import relationship
from app.db.base import Base
from app.models.activity import ActivityCategory, ActivityLevel


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    organizer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    department_id = Column(Integer, ForeignKey("departments.id"), nullable=True)
    event_date = Column(Date, nullable=False)
    level = Column(Enum(ActivityLevel), nullable=False)
    category = Column(Enum(ActivityCategory), nullable=False)
    qr_token = Column(String(128), unique=True, nullable=False)
    qr_expires_at = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    organizer = relationship("User")
    department = relationship("Department")
    attendances = relationship("Attendance", back_populates="event", cascade="all, delete-orphan")
    activities = relationship("Activity", back_populates="event")
