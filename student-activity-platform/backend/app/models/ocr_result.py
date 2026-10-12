import enum
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, Enum, ForeignKey, JSON, func
from sqlalchemy.orm import relationship
from app.db.base import Base


class OCRStatus(str, enum.Enum):
    queued = "queued"
    done = "done"
    failed = "failed"


class OCRResult(Base):
    __tablename__ = "ocr_results"

    id = Column(Integer, primary_key=True, index=True)
    activity_id = Column(Integer, ForeignKey("activities.id"), unique=True, nullable=False)
    extracted_text = Column(Text, nullable=True)
    extracted_name = Column(String(255), nullable=True)
    extracted_event = Column(String(255), nullable=True)
    extracted_date = Column(String(100), nullable=True)
    match_score_name = Column(Float, nullable=True)
    match_score_event = Column(Float, nullable=True)
    match_score_date = Column(Float, nullable=True)
    overall_confidence = Column(Float, nullable=True)
    mismatch_flags = Column(JSON, default=list)
    processed_at = Column(DateTime(timezone=True), nullable=True)
    status = Column(Enum(OCRStatus), default=OCRStatus.queued, nullable=False)

    activity = relationship("Activity", back_populates="ocr_result")
