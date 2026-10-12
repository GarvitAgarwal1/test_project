"""Portfolio PDF generation service using ReportLab."""
import os
import io
import secrets
from datetime import datetime
from sqlalchemy.orm import Session
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch, cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
from reportlab.lib.enums import TA_CENTER, TA_LEFT

from app.models.activity import Activity, ActivityStatus
from app.models.portfolio import Portfolio
from app.models.user import User
from app.models.verification import Verification
from app.services.qr_service import generate_qr_image
from app.services.scoring_service import get_student_total_points
from app.core.config import settings


CATEGORY_DISPLAY = {
    "technical": "Technical",
    "hackathon": "Hackathon",
    "sports": "Sports",
    "cultural": "Cultural",
    "ncc_nss": "NCC/NSS",
    "social_service": "Social Service",
    "certification": "Certification",
    "internship": "Internship",
    "publication": "Publication",
    "workshop": "Workshop",
    "other": "Other",
}


def generate_portfolio_pdf(db: Session, student_id: int, base_url: str = "http://localhost:8000") -> Portfolio:
    """Generate a professional portfolio PDF for a student."""
    student = db.query(User).filter(User.id == student_id).first()
    if not student:
        raise ValueError("Student not found")

    activities = db.query(Activity).filter(
        Activity.student_id == student_id,
        Activity.status == ActivityStatus.APPROVED,
    ).order_by(Activity.activity_date.desc()).all()

    total_points = get_student_total_points(db, student_id)

    # Create or update portfolio record
    portfolio = db.query(Portfolio).filter(Portfolio.student_id == student_id).first()
    if portfolio:
        portfolio.version += 1
        portfolio.generated_at = datetime.utcnow()
    else:
        portfolio = Portfolio(
            student_id=student_id,
            verification_token=secrets.token_urlsafe(32),
            version=1,
        )
        db.add(portfolio)
        db.flush()

    verify_url = f"{base_url}/verify/{portfolio.verification_token}"

    # Generate QR code image
    qr_bytes = generate_qr_image(verify_url)
    qr_path = os.path.join(settings.UPLOAD_DIR, f"qr_portfolio_{student_id}.png")
    with open(qr_path, "wb") as f:
        f.write(qr_bytes)

    # Generate PDF
    pdf_filename = f"portfolio_{student_id}_v{portfolio.version}.pdf"
    pdf_path = os.path.join(settings.UPLOAD_DIR, pdf_filename)

    doc = SimpleDocTemplate(pdf_path, pagesize=A4, rightMargin=1*cm, leftMargin=1*cm, topMargin=1*cm, bottomMargin=1*cm)
    styles = getSampleStyleSheet()
    story = []

    # Custom styles
    title_style = ParagraphStyle('CustomTitle', parent=styles['Title'], fontSize=20, spaceAfter=6, textColor=colors.HexColor("#1e3a5f"))
    subtitle_style = ParagraphStyle('Subtitle', parent=styles['Normal'], fontSize=12, spaceAfter=12, textColor=colors.HexColor("#555555"), alignment=TA_CENTER)
    heading_style = ParagraphStyle('SectionHeading', parent=styles['Heading2'], fontSize=14, spaceAfter=8, textColor=colors.HexColor("#1e3a5f"), borderWidth=1, borderColor=colors.HexColor("#1e3a5f"), borderPadding=4)

    # Header
    story.append(Paragraph("Student Activity Portfolio", title_style))
    story.append(Paragraph("Centralized Student Activity Platform — Verified Record", subtitle_style))
    story.append(Spacer(1, 12))

    # Student Info
    dept_name = student.department.name if student.department else "N/A"
    info_data = [
        ["Student Name:", student.full_name, "Department:", dept_name],
        ["Enrollment No:", student.enrollment_no or "N/A", "Year:", str(student.year or "N/A")],
        ["Email:", student.email, "Total Points:", str(total_points)],
        ["Generated:", datetime.utcnow().strftime("%d %b %Y, %H:%M"), "Activities:", str(len(activities))],
    ]
    info_table = Table(info_data, colWidths=[100, 170, 100, 170])
    info_table.setStyle(TableStyle([
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 20))

    # Activities grouped by category
    categories_used = set(a.category.value for a in activities)
    for cat in sorted(categories_used):
        cat_activities = [a for a in activities if a.category.value == cat]
        story.append(Paragraph(f"{CATEGORY_DISPLAY.get(cat, cat)} ({len(cat_activities)})", heading_style))

        table_data = [["#", "Title", "Level", "Date", "Organizer", "Points"]]
        for i, act in enumerate(cat_activities, 1):
            table_data.append([
                str(i),
                act.title[:40],
                act.level.value.title(),
                str(act.activity_date),
                act.organizer[:30],
                str(act.points_awarded or 0),
            ])

        t = Table(table_data, colWidths=[25, 160, 60, 75, 120, 45])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1e3a5f")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor("#f8f9fa"), colors.white]),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#dee2e6")),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(t)
        story.append(Spacer(1, 12))

    # QR Code and verification
    story.append(Spacer(1, 20))
    story.append(Paragraph("Verification", heading_style))
    story.append(Paragraph(f"Scan the QR code or visit the URL below to verify this portfolio:", styles['Normal']))
    story.append(Spacer(1, 8))

    if os.path.exists(qr_path):
        qr_img = RLImage(qr_path, width=1.5*inch, height=1.5*inch)
        story.append(qr_img)

    story.append(Spacer(1, 4))
    story.append(Paragraph(f'<font size="8" color="#666666">{verify_url}</font>', styles['Normal']))
    story.append(Spacer(1, 8))
    story.append(Paragraph(f'<font size="8" color="#999999">This is a system-generated document. Authenticity can be verified via the QR code above. Version {portfolio.version}.</font>', styles['Normal']))

    doc.build(story)

    portfolio.file_path = pdf_filename
    db.commit()
    db.refresh(portfolio)
    return portfolio
