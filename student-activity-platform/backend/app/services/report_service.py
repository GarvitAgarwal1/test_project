"""Reporting service for accreditation data export."""
import csv
import io
import os
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

from app.models.activity import Activity, ActivityStatus
from app.models.department import Department
from app.models.user import User
from app.core.config import settings


def generate_accreditation_report(db: Session, academic_year: str, department_id: int = None, format: str = "pdf") -> str:
    """Generate NAAC/NIRF style accreditation report."""
    # Simplified academic year filter: just take activities from that year for demo purposes
    # E.g., "2023-2024"
    try:
        start_year = int(academic_year.split("-")[0])
        start_date = f"{start_year}-07-01"
        end_date = f"{start_year + 1}-06-30"
    except Exception:
        start_date = "2000-01-01"
        end_date = "2100-01-01"

    query = db.query(Activity).join(User).filter(
        Activity.status == ActivityStatus.APPROVED,
        Activity.activity_date >= start_date,
        Activity.activity_date <= end_date
    )

    dept_name = "All Departments"
    if department_id:
        query = query.filter(User.department_id == department_id)
        dept = db.query(Department).filter(Department.id == department_id).first()
        if dept:
            dept_name = dept.name

    activities = query.all()

    filename = f"report_{academic_year}_{department_id or 'all'}_{datetime.utcnow().timestamp()}.{format}"
    filepath = os.path.join(settings.UPLOAD_DIR, filename)

    if format == "csv":
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Student Name", "Enrollment No", "Department", "Activity Title", "Category", "Level", "Date", "Organizer", "Points"])
            for act in activities:
                writer.writerow([
                    act.student.full_name if act.student else "",
                    act.student.enrollment_no if act.student else "",
                    act.student.department.name if act.student and act.student.department else "",
                    act.title,
                    act.category.value,
                    act.level.value,
                    str(act.activity_date),
                    act.organizer,
                    act.points_awarded or 0
                ])
        return filename
    else:
        # PDF format
        doc = SimpleDocTemplate(filepath, pagesize=landscape(A4))
        story = []
        
        # Add a simple table for the report
        data = [["Student Name", "Enrollment No", "Activity Title", "Category", "Level", "Date", "Points"]]
        for act in activities:
            data.append([
                (act.student.full_name[:20] if act.student else ""),
                (act.student.enrollment_no or ""),
                act.title[:30],
                act.category.value,
                act.level.value,
                str(act.activity_date),
                str(act.points_awarded or 0)
            ])
            
        t = Table(data)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(t)
        doc.build(story)
        return filename
