import os
import sys
from datetime import date
from sqlalchemy.orm import Session
from app.db.session import SessionLocal, engine
from app.db.base import Base
from app.models.user import User, UserRole
from app.models.department import Department
from app.models.score_rule import ScoreRule
from app.core.security import hash_password
from app.services.scoring_service import seed_default_rules

def seed():
    db = SessionLocal()
    try:
        # Create departments
        deps = [("Computer Science", "CSE"), ("Information Tech", "IT"), ("Electronics", "ECE"), ("Mechanical", "ME")]
        db_deps = []
        for name, code in deps:
            d = db.query(Department).filter_by(code=code).first()
            if not d:
                d = Department(name=name, code=code)
                db.add(d)
                db.flush()
            db_deps.append(d)

        db.commit()
        
        # Create users
        if not db.query(User).filter_by(email="admin@demo.com").first():
            db.add(User(full_name="Admin User", email="admin@demo.com", password_hash=hash_password("Admin@123"), role=UserRole.admin, is_active=True))
            
        if not db.query(User).filter_by(email="faculty1@demo.com").first():
            db.add(User(full_name="Faculty One", email="faculty1@demo.com", password_hash=hash_password("Faculty@123"), role=UserRole.faculty, department_id=db_deps[0].id, is_active=True))
            
        if not db.query(User).filter_by(email="student1@demo.com").first():
            db.add(User(full_name="Student One", email="student1@demo.com", password_hash=hash_password("Student@123"), role=UserRole.student, department_id=db_deps[0].id, enrollment_no="ENR001", year=2, is_active=True))

        db.commit()

        # Seed default scoring rules
        seed_default_rules(db)
        
        print("Database seeded successfully with demo credentials:")
        print("Admin: admin@demo.com / Admin@123")
        print("Faculty: faculty1@demo.com / Faculty@123")
        print("Student: student1@demo.com / Student@123")

    finally:
        db.close()

if __name__ == "__main__":
    seed()
