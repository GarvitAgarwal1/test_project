"""Celery tasks for background processing."""
from app.core.celery_app import celery_app
from app.db.session import SessionLocal
from app.services.ocr_service import process_certificate
from app.services.anomaly_service import run_anomaly_checks, has_medium_or_high_flags
from app.models.activity import Activity, ActivityStatus


@celery_app.task
def process_activity_proof(activity_id: int):
    """Run OCR and anomaly checks on a newly submitted activity."""
    db = SessionLocal()
    try:
        activity = db.query(Activity).filter(Activity.id == activity_id).first()
        if not activity:
            return
        
        # 1. Run OCR
        ocr_result = process_certificate(db, activity_id)
        
        # 2. Run Anomaly Checks
        flags = run_anomaly_checks(db, activity_id)
        
        # 3. Determine new status
        # If any medium/high anomaly or low OCR confidence (which triggers an anomaly flag), set to FLAGGED
        has_flags = has_medium_or_high_flags(db, activity_id)
        if has_flags:
            activity.status = ActivityStatus.FLAGGED
        else:
            activity.status = ActivityStatus.PENDING
            
        db.commit()
    finally:
        db.close()


@celery_app.task
def generate_portfolio_task(student_id: int):
    """Generate portfolio PDF asynchronously."""
    db = SessionLocal()
    try:
        from app.services.portfolio_service import generate_portfolio_pdf
        generate_portfolio_pdf(db, student_id)
    finally:
        db.close()


@celery_app.task
def generate_accreditation_report_task(academic_year: str, department_id: int, format: str):
    """Generate report asynchronously."""
    db = SessionLocal()
    try:
        from app.services.report_service import generate_accreditation_report
        # We don't have a place to store report generation status yet, 
        # so for this project we'll just generate it and maybe store the result somewhere if needed.
        # Actually a better design would be a Reports model, but let's keep it simple for now.
        generate_accreditation_report(db, academic_year, department_id, format)
    finally:
        db.close()
