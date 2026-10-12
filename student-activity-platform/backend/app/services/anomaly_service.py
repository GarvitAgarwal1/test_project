"""Anomaly detection service — rule-based engine for flagging suspicious activities."""
from datetime import datetime, timedelta, date
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.activity import Activity, ActivityStatus
from app.models.anomaly_flag import AnomalyFlag, AnomalySeverity
from app.models.ocr_result import OCRResult


BURST_THRESHOLD = 5  # Max submissions in 24 hours before flagging
OCR_CONFIDENCE_THRESHOLD = 40.0  # Below this triggers LOW_OCR_CONFIDENCE
LEVEL_KEYWORDS = {
    "national": ["national", "india", "bharath", "all india", "nit", "iit", "university"],
    "international": ["international", "global", "world", "ieee", "acm", "springer"],
    "state": ["state", "regional", "zonal", "district"],
}


def run_anomaly_checks(db: Session, activity_id: int) -> List[AnomalyFlag]:
    """Run all anomaly detection rules on an activity."""
    activity = db.query(Activity).filter(Activity.id == activity_id).first()
    if not activity:
        return []

    # Clear existing flags for this activity (for resubmission)
    db.query(AnomalyFlag).filter(AnomalyFlag.activity_id == activity_id).delete()
    db.commit()

    flags = []

    # Rule 1: DUPLICATE_FILE - same proof hash used by another activity
    if activity.proof_file_hash:
        duplicate = db.query(Activity).filter(
            Activity.proof_file_hash == activity.proof_file_hash,
            Activity.id != activity.id,
        ).first()
        if duplicate:
            severity = AnomalySeverity.high
            msg = f"Same proof file (SHA-256 match) already used in activity #{duplicate.id}"
            if duplicate.student_id != activity.student_id:
                msg += f" by a different student (ID: {duplicate.student_id})"
                flags.append(_create_flag(db, activity_id, "SAME_CERT_DIFFERENT_STUDENT", severity, msg))
            else:
                flags.append(_create_flag(db, activity_id, "DUPLICATE_FILE", severity, msg))

    # Rule 2: FUTURE_DATE
    if activity.activity_date and activity.activity_date > date.today():
        flags.append(_create_flag(
            db, activity_id, "FUTURE_DATE", AnomalySeverity.high,
            f"Activity date {activity.activity_date} is in the future"
        ))

    # Rule 3: VERY_OLD_DATE - older than 5 years
    if activity.activity_date:
        five_years_ago = date.today() - timedelta(days=5*365)
        if activity.activity_date < five_years_ago:
            flags.append(_create_flag(
                db, activity_id, "VERY_OLD_DATE", AnomalySeverity.low,
                f"Activity date {activity.activity_date} is more than 5 years ago"
            ))

    # Rule 4: DATE_OVERLAP - same student, same date, different organizer
    if activity.activity_date:
        overlaps = db.query(Activity).filter(
            Activity.student_id == activity.student_id,
            Activity.activity_date == activity.activity_date,
            Activity.id != activity.id,
            Activity.organizer != activity.organizer,
        ).all()
        if overlaps:
            flags.append(_create_flag(
                db, activity_id, "DATE_OVERLAP", AnomalySeverity.medium,
                f"Student has {len(overlaps)} other activit{'y' if len(overlaps)==1 else 'ies'} on the same date ({activity.activity_date}) with different organizers"
            ))

    # Rule 5: BURST_SUBMISSIONS - more than N submissions in 24 hours
    yesterday = datetime.utcnow() - timedelta(hours=24)
    recent_count = db.query(func.count(Activity.id)).filter(
        Activity.student_id == activity.student_id,
        Activity.created_at >= yesterday,
    ).scalar()
    if recent_count and recent_count > BURST_THRESHOLD:
        flags.append(_create_flag(
            db, activity_id, "BURST_SUBMISSIONS", AnomalySeverity.low,
            f"Student submitted {recent_count} activities in the last 24 hours (threshold: {BURST_THRESHOLD})"
        ))

    # Rule 6: LEVEL_MISMATCH - claims high level but OCR shows no supporting keywords
    ocr = db.query(OCRResult).filter(OCRResult.activity_id == activity_id).first()
    if ocr and ocr.extracted_text and activity.level.value in ("national", "international"):
        text_lower = ocr.extracted_text.lower()
        keywords = LEVEL_KEYWORDS.get(activity.level.value, [])
        if not any(kw in text_lower for kw in keywords):
            flags.append(_create_flag(
                db, activity_id, "LEVEL_MISMATCH", AnomalySeverity.medium,
                f"Claims {activity.level.value} level but certificate text contains no supporting keywords"
            ))

    # Rule 7: LOW_OCR_CONFIDENCE
    if ocr and ocr.overall_confidence is not None and ocr.overall_confidence < OCR_CONFIDENCE_THRESHOLD:
        flags.append(_create_flag(
            db, activity_id, "LOW_OCR_CONFIDENCE", AnomalySeverity.medium,
            f"OCR confidence is {ocr.overall_confidence:.1f}% (threshold: {OCR_CONFIDENCE_THRESHOLD}%)"
        ))

    return flags


def _create_flag(db: Session, activity_id: int, rule_code: str, severity: AnomalySeverity, message: str) -> AnomalyFlag:
    """Create and persist an anomaly flag."""
    flag = AnomalyFlag(
        activity_id=activity_id,
        rule_code=rule_code,
        severity=severity,
        message=message,
    )
    db.add(flag)
    db.commit()
    db.refresh(flag)
    return flag


def has_medium_or_high_flags(db: Session, activity_id: int) -> bool:
    """Check if activity has any medium or high severity flags."""
    count = db.query(func.count(AnomalyFlag.id)).filter(
        AnomalyFlag.activity_id == activity_id,
        AnomalyFlag.severity.in_([AnomalySeverity.medium, AnomalySeverity.high]),
    ).scalar()
    return count > 0
