from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.session import get_db
from app.models.activity import Activity, ActivityStatus
from app.models.portfolio import Portfolio
from app.schemas.activity import PublicVerifyResponse

router = APIRouter()

@router.get("/verify/{verification_token}", response_model=PublicVerifyResponse)
def verify_portfolio(
    verification_token: str,
    db: Session = Depends(get_db)
):
    """Publicly verify a student's portfolio using the token."""
    portfolio = db.query(Portfolio).filter(Portfolio.verification_token == verification_token).first()
    if not portfolio:
        raise HTTPException(status_code=404, detail="Invalid verification token")
        
    student = portfolio.student
    activities = db.query(Activity).filter(
        Activity.student_id == student.id,
        Activity.status == ActivityStatus.APPROVED
    ).order_by(Activity.activity_date.desc()).all()
    
    total_points = db.query(func.coalesce(func.sum(Activity.points_awarded), 0)).filter(
        Activity.student_id == student.id,
        Activity.status == ActivityStatus.APPROVED
    ).scalar()
    
    act_list = [
        {
            "title": a.title,
            "category": a.category.value,
            "level": a.level.value,
            "date": str(a.activity_date),
            "organizer": a.organizer,
            "points": a.points_awarded
        } for a in activities
    ]
    
    return {
        "student_name": student.full_name,
        "department": student.department.name if student.department else None,
        "enrollment_no": student.enrollment_no,
        "total_points": int(total_points),
        "activities": act_list,
        "generated_at": portfolio.generated_at,
        "authenticity": "VERIFIED"
    }
