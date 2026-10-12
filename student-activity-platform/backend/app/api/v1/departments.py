from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.models.department import Department
from app.models.user import User
from app.schemas.department import DepartmentCreate, DepartmentResponse, DepartmentListResponse
from app.core.deps import get_current_active_user, require_roles

router = APIRouter()

@router.get("", response_model=DepartmentListResponse)
def list_departments(
    db: Session = Depends(get_db)
):
    """List all departments (publicly accessible for registration dropdowns)."""
    items = db.query(Department).all()
    return {"items": items, "total": len(items)}

@router.post("", response_model=DepartmentResponse)
def create_department(
    dept_in: DepartmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("admin"))
):
    """Create a new department (admin only)."""
    dept = db.query(Department).filter(Department.name == dept_in.name).first()
    if dept:
        raise HTTPException(status_code=400, detail="Department with this name already exists")
        
    db_dept = Department(name=dept_in.name, code=dept_in.code)
    db.add(db_dept)
    db.commit()
    db.refresh(db_dept)
    return db_dept
