from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


class UserCreate(BaseModel):
    """Admin creating faculty/admin users."""
    full_name: str = Field(..., min_length=2, max_length=200)
    email: str = Field(..., min_length=5)
    password: str = Field(..., min_length=8)
    role: str = Field(..., pattern="^(student|faculty|admin)$")
    department_id: Optional[int] = None
    enrollment_no: Optional[str] = None
    year: Optional[int] = None


class UserUpdate(BaseModel):
    """Update user fields."""
    full_name: Optional[str] = None
    role: Optional[str] = None
    department_id: Optional[int] = None
    is_active: Optional[bool] = None
    year: Optional[int] = None


class UserResponse(BaseModel):
    id: int
    full_name: str
    email: str
    role: str
    department_id: Optional[int] = None
    enrollment_no: Optional[str] = None
    year: Optional[int] = None
    is_active: bool
    created_at: Optional[datetime] = None
    department_name: Optional[str] = None

    model_config = {"from_attributes": True}


class UserListResponse(BaseModel):
    items: List[UserResponse]
    total: int
    page: int
    page_size: int
