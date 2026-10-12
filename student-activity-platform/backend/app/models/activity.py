import enum
from sqlalchemy import Column, Integer, String, Text, Date, DateTime, Enum, ForeignKey, Index, func
from sqlalchemy.orm import relationship
from app.db.base import Base


class ActivityCategory(str, enum.Enum):
    technical = "technical"
    hackathon = "hackathon"
    sports = "sports"
    cultural = "cultural"
    ncc_nss = "ncc_nss"
    social_service = "social_service"
    certification = "certification"
    internship = "internship"
    publication = "publication"
    workshop = "workshop"
    other = "other"


class ActivityLevel(str, enum.Enum):
    college = "college"
    state = "state"
    national = "national"
    international = "international"


class ActivityStatus(str, enum.Enum):
    PENDING = "PENDING"
    FLAGGED = "FLAGGED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class ActivitySource(str, enum.Enum):
    manual = "manual"
    qr_checkin = "qr_checkin"


class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    category = Column(Enum(ActivityCategory), nullable=False)
    level = Column(Enum(ActivityLevel), nullable=False)
    activity_date = Column(Date, nullable=False)
    organizer = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    position_or_result = Column(String(100), nullable=True)
    proof_file_path = Column(String(500), nullable=True)
    proof_file_hash = Column(String(64), nullable=True)
    proof_mime_type = Column(String(50), nullable=True)
    status = Column(Enum(ActivityStatus), default=ActivityStatus.PENDING, nullable=False)
    points_awarded = Column(Integer, nullable=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=True)
    source = Column(Enum(ActivitySource), default=ActivitySource.manual, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    student = relationship("User", back_populates="activities")
    verifications = relationship("Verification", back_populates="activity", cascade="all, delete-orphan")
    ocr_result = relationship("OCRResult", back_populates="activity", uselist=False, cascade="all, delete-orphan")
    anomaly_flags = relationship("AnomalyFlag", back_populates="activity", cascade="all, delete-orphan")
    event = relationship("Event", back_populates="activities")

    __table_args__ = (
        Index("ix_activities_student_id", "student_id"),
        Index("ix_activities_status", "status"),
        Index("ix_activities_category", "category"),
        Index("ix_activities_activity_date", "activity_date"),
    )
