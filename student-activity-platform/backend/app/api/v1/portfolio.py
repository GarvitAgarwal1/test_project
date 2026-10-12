from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User
from app.models.portfolio import Portfolio
from app.schemas.activity import PortfolioResponse
from app.core.deps import require_roles
from app.tasks.background_tasks import generate_portfolio_task

router = APIRouter()

@router.post("/generate")
def generate_portfolio(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("student"))
):
    """Trigger background generation of portfolio."""
    generate_portfolio_task.delay(current_user.id)
    return {"message": "Portfolio generation queued"}


@router.get("/mine", response_model=PortfolioResponse)
def get_my_portfolio(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("student"))
):
    """Get the current student's portfolio status and info."""
    portfolio = db.query(Portfolio).filter(Portfolio.student_id == current_user.id).first()
    if not portfolio:
        raise HTTPException(status_code=404, detail="No portfolio found. Generate one first.")
        
    return portfolio
