from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from app.db.session import get_db
from app.models.user import User
from app.models.activity import Activity, ActivityStatus
from app.models.verification import Verification
from app.schemas.activity import ActivityListResponse, VerificationDecisionRequest, ActivityResponse
from app.core.deps import require_roles
from app.services.audit_service import log as audit_log
from app.services.scoring_service import calculate_points

router = APIRouter()

@router.get("/queue", response_model=ActivityListResponse)
def get_verification_queue(
    status: Optional[str] = None,
    category: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("faculty", "admin"))
):
    """Get the queue of pending/flagged activities for review."""
    query = db.query(Activity).filter(Activity.status.in_([ActivityStatus.PENDING, ActivityStatus.FLAGGED]))
    
    if current_user.role.value == "faculty":
        # Faculty see their department's students
        if current_user.department_id:
            query = query.join(User).filter(User.department_id == current_user.department_id)
            
    if status:
        query = query.filter(Activity.status == status)
    if category:
        query = query.filter(Activity.category == category)
        
    total = query.count()
    items = query.order_by(Activity.created_at.asc()).offset((page - 1) * page_size).limit(page_size).all()
    
    return {"items": items, "total": total, "page": page, "page_size": page_size}


@router.post("/{activity_id}/decision", response_model=ActivityResponse)
def make_decision(
    activity_id: int,
    decision_in: VerificationDecisionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("faculty", "admin"))
):
    """Approve or reject an activity."""
    activity = db.query(Activity).filter(Activity.id == activity_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
        
    if activity.status not in [ActivityStatus.PENDING, ActivityStatus.FLAGGED]:
        raise HTTPException(status_code=400, detail=f"Activity is already {activity.status.value}")
        
    if decision_in.decision == "REJECTED" and not decision_in.remarks:
        raise HTTPException(status_code=400, detail="Remarks are required for rejection")
        
    # Record verification decision
    verification = Verification(
        activity_id=activity.id,
        verifier_id=current_user.id,
        decision=decision_in.decision,
        remarks=decision_in.remarks
    )
    db.add(verification)
    
    # Update activity status and points
    if decision_in.decision == "APPROVED":
        activity.status = ActivityStatus.APPROVED
        activity.points_awarded = calculate_points(db, activity)
        action_name = "ACTIVITY_APPROVED"
    else:
        activity.status = ActivityStatus.REJECTED
        activity.points_awarded = None
        action_name = "ACTIVITY_REJECTED"
        
    db.commit()
    db.refresh(activity)
    
    audit_log(db, actor_id=current_user.id, action=action_name, entity_type="ACTIVITY", entity_id=activity.id, details={"remarks": decision_in.remarks})
    
    return activity
