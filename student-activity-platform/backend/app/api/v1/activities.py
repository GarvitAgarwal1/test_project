from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date

from app.db.session import get_db
from app.models.user import User
from app.models.activity import Activity, ActivityStatus, ActivitySource
from app.schemas.activity import ActivityResponse, ActivityListResponse, ActivityCreate
from app.core.deps import get_current_active_user, require_roles
from app.services.file_service import save_upload, validate_file
from app.services.audit_service import log as audit_log
from app.tasks.background_tasks import process_activity_proof

router = APIRouter()

@router.post("", response_model=ActivityResponse)
async def submit_activity(
    title: str = Form(...),
    category: str = Form(...),
    level: str = Form(...),
    activity_date: date = Form(...),
    organizer: str = Form(...),
    description: Optional[str] = Form(None),
    position_or_result: Optional[str] = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("student"))
):
    """Submit a new activity with proof file."""
    validate_file(file)
    file_info = await save_upload(file)

    activity = Activity(
        student_id=current_user.id,
        title=title,
        category=category,
        level=level,
        activity_date=activity_date,
        organizer=organizer,
        description=description,
        position_or_result=position_or_result,
        proof_file_path=file_info["file_path"],
        proof_file_hash=file_info["file_hash"],
        proof_mime_type=file_info["mime_type"],
        status=ActivityStatus.PENDING,
        source=ActivitySource.manual
    )
    db.add(activity)
    db.commit()
    db.refresh(activity)

    audit_log(db, actor_id=current_user.id, action="ACTIVITY_SUBMITTED", entity_type="ACTIVITY", entity_id=activity.id)

    # Queue background task for OCR and anomaly checks
    process_activity_proof.delay(activity.id)

    return activity


@router.get("/mine", response_model=ActivityListResponse)
def get_my_activities(
    status: Optional[str] = None,
    category: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("student"))
):
    """List student's own activities."""
    query = db.query(Activity).filter(Activity.student_id == current_user.id)
    if status:
        query = query.filter(Activity.status == status)
    if category:
        query = query.filter(Activity.category == category)
    
    total = query.count()
    items = query.order_by(Activity.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    
    return {"items": items, "total": total, "page": page, "page_size": page_size}


@router.get("/{activity_id}", response_model=ActivityResponse)
def get_activity(
    activity_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get single activity details."""
    activity = db.query(Activity).filter(Activity.id == activity_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
        
    if current_user.role.value == "student" and activity.student_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this activity")
        
    return activity
