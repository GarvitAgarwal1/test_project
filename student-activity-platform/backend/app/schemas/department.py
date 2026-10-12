from pydantic import BaseModel, Field
from typing import List, Optional


class DepartmentCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    code: str = Field(..., min_length=2, max_length=20)


class DepartmentResponse(BaseModel):
    id: int
    name: str
    code: str

    model_config = {"from_attributes": True}


class DepartmentListResponse(BaseModel):
    items: List[DepartmentResponse]
    total: int
