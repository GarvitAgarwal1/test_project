from fastapi import APIRouter
from app.api.v1 import auth, users, departments, activities, verification, events, portfolio, public

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(departments.router, prefix="/departments", tags=["departments"])
api_router.include_router(activities.router, prefix="/activities", tags=["activities"])
api_router.include_router(verification.router, prefix="/verification", tags=["verification"])
api_router.include_router(events.router, prefix="/events", tags=["events"])
api_router.include_router(portfolio.router, prefix="/portfolio", tags=["portfolio"])
api_router.include_router(public.router, prefix="/public", tags=["public"])
