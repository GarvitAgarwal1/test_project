from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime


class ActivityCreate(BaseModel):
    title: str = Field(..., min_length=2, max_length=255)
    category: str
    level: str
    activity_date: date
    organizer: str = Field(..., min_length=2, max_length=255)
    description: Optional[str] = None
    position_or_result: Optional[str] = None


class ActivityUpdate(BaseModel):
    title: Optional[str] = None
    category: Optional[str] = None
    level: Optional[str] = None
    activity_date: Optional[date] = None
    organizer: Optional[str] = None
    description: Optional[str] = None
    position_or_result: Optional[str] = None


class OCRResultResponse(BaseModel):
    id: int
    extracted_text: Optional[str] = None
    extracted_name: Optional[str] = None
    extracted_event: Optional[str] = None
    extracted_date: Optional[str] = None
    match_score_name: Optional[float] = None
    match_score_event: Optional[float] = None
    match_score_date: Optional[float] = None
    overall_confidence: Optional[float] = None
    mismatch_flags: Optional[list] = None
    status: str
    processed_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class AnomalyFlagResponse(BaseModel):
    id: int
    rule_code: str
    severity: str
    message: str
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class VerificationResponse(BaseModel):
    id: int
    verifier_id: int
    verifier_name: Optional[str] = None
    decision: str
    remarks: Optional[str] = None
    decided_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ActivityResponse(BaseModel):
    id: int
    student_id: int
    student_name: Optional[str] = None
    department_name: Optional[str] = None
    title: str
    category: str
    level: str
    activity_date: date
    organizer: str
    description: Optional[str] = None
    position_or_result: Optional[str] = None
    proof_file_path: Optional[str] = None
    proof_mime_type: Optional[str] = None
    status: str
    points_awarded: Optional[int] = None
    event_id: Optional[int] = None
    source: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    ocr_result: Optional[OCRResultResponse] = None
    anomaly_flags: Optional[List[AnomalyFlagResponse]] = None
    verifications: Optional[List[VerificationResponse]] = None

    model_config = {"from_attributes": True}


class ActivityListResponse(BaseModel):
    items: List[ActivityResponse]
    total: int
    page: int
    page_size: int


class VerificationDecisionRequest(BaseModel):
    decision: str = Field(..., pattern="^(APPROVED|REJECTED)$")
    remarks: Optional[str] = None


class BulkApproveRequest(BaseModel):
    activity_ids: List[int]


class EventCreate(BaseModel):
    title: str = Field(..., min_length=2, max_length=255)
    description: Optional[str] = None
    department_id: Optional[int] = None
    event_date: date
    level: str
    category: str
    qr_expires_hours: Optional[int] = 24


class EventResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    organizer_id: int
    organizer_name: Optional[str] = None
    department_id: Optional[int] = None
    event_date: date
    level: str
    category: str
    qr_token: Optional[str] = None
    qr_expires_at: Optional[datetime] = None
    is_active: bool
    created_at: Optional[datetime] = None
    attendee_count: Optional[int] = 0

    model_config = {"from_attributes": True}


class EventListResponse(BaseModel):
    items: List[EventResponse]
    total: int


class CheckinRequest(BaseModel):
    qr_token: str


class ScoreRuleResponse(BaseModel):
    id: int
    category: str
    base_points: int
    level_multiplier: dict
    position_bonus: dict
    active: bool

    model_config = {"from_attributes": True}


class ScoreRuleUpdate(BaseModel):
    base_points: Optional[int] = None
    level_multiplier: Optional[dict] = None
    position_bonus: Optional[dict] = None
    active: Optional[bool] = None


class AuditLogResponse(BaseModel):
    id: int
    actor_id: Optional[int] = None
    action: str
    entity_type: str
    entity_id: Optional[int] = None
    details: Optional[dict] = None
    ip_address: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class AuditLogListResponse(BaseModel):
    items: List[AuditLogResponse]
    total: int
    page: int
    page_size: int


class PortfolioResponse(BaseModel):
    id: int
    student_id: int
    verification_token: str
    file_path: Optional[str] = None
    generated_at: Optional[datetime] = None
    version: int
    status: Optional[str] = "ready"

    model_config = {"from_attributes": True}


class ReportRequest(BaseModel):
    academic_year: str = Field(..., pattern="^\\d{4}-\\d{4}$")
    department_id: Optional[int] = None
    format: str = Field(default="pdf", pattern="^(csv|pdf)$")


class PublicVerifyResponse(BaseModel):
    student_name: str
    department: Optional[str] = None
    enrollment_no: Optional[str] = None
    total_points: int
    activities: List[dict]
    generated_at: Optional[datetime] = None
    authenticity: str = "VERIFIED"
