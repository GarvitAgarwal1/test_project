from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from app.db.base import Base


class Portfolio(Base):
    __tablename__ = "portfolios"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    verification_token = Column(String(128), unique=True, nullable=False)
    file_path = Column(String(500), nullable=True)
    generated_at = Column(DateTime(timezone=True), server_default=func.now())
    version = Column(Integer, default=1)
