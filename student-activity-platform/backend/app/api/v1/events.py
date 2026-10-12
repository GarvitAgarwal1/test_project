import secrets
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.models.event import Event
from app.models.attendance import Attendance
from app.models.activity import Activity, ActivityStatus, ActivitySource
from app.schemas.activity import EventCreate, EventResponse, EventListResponse, CheckinRequest
from app.core.deps import require_roles, get_current_active_user
from app.services.audit_service import log as audit_log
from app.services.qr_service import generate_qr_image

router = APIRouter()

@router.post("", response_model=EventResponse)
def create_event(
    event_in: EventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("faculty", "admin"))
):
    """Create a new event with a secure QR token."""
    token = secrets.token_urlsafe(32)
    expires = datetime.utcnow() + timedelta(hours=event_in.qr_expires_hours or 24)
    
    event = Event(
        title=event_in.title,
        description=event_in.description,
        organizer_id=current_user.id,
        department_id=event_in.department_id,
        event_date=event_in.event_date,
        level=event_in.level,
        category=event_in.category,
        qr_token=token,
        qr_expires_at=expires,
        is_active=True
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    
    audit_log(db, actor_id=current_user.id, action="EVENT_CREATED", entity_type="EVENT", entity_id=event.id)
    return event


@router.get("", response_model=EventListResponse)
def list_events(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """List events."""
    items = db.query(Event).order_by(Event.created_at.desc()).all()
    # Simple attendee count attachment for response
    for item in items:
        item.attendee_count = db.query(Attendance).filter(Attendance.event_id == item.id).count()
        item.organizer_name = item.organizer.full_name if item.organizer else None
    return {"items": items, "total": len(items)}


@router.get("/{event_id}/qr")
def get_event_qr(
    event_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("faculty", "admin"))
):
    """Return the QR code PNG image for the event."""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
        
    qr_bytes = generate_qr_image(event.qr_token)
    return Response(content=qr_bytes, media_type="image/png")


@router.post("/checkin")
def qr_checkin(
    checkin_in: CheckinRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("student"))
):
    """Student scans event QR token to check in."""
    event = db.query(Event).filter(Event.qr_token == checkin_in.qr_token).first()
    if not event:
        raise HTTPException(status_code=404, detail="Invalid QR token")
        
    if not event.is_active or (event.qr_expires_at and event.qr_expires_at < datetime.utcnow()):
        raise HTTPException(status_code=400, detail="Event QR is inactive or expired")
        
    # Check if already checked in
    existing = db.query(Attendance).filter(
        Attendance.event_id == event.id,
        Attendance.student_id == current_user.id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Already checked in to this event")
        
    # Create activity automatically
    activity = Activity(
        student_id=current_user.id,
        title=f"Attended: {event.title}",
        category=event.category,
        level=event.level,
        activity_date=event.event_date,
        organizer=event.organizer.full_name if event.organizer else "Unknown",
        status=ActivityStatus.PENDING,
        source=ActivitySource.qr_checkin,
        event_id=event.id
    )
    db.add(activity)
    db.commit()
    db.refresh(activity)
    
    # Create attendance
    attendance = Attendance(
        event_id=event.id,
        student_id=current_user.id,
        activity_id=activity.id
    )
    db.add(attendance)
    db.commit()
    
    audit_log(db, actor_id=current_user.id, action="QR_CHECKIN", entity_type="EVENT", entity_id=event.id)
    
    return {"message": "Successfully checked in", "activity_id": activity.id}
