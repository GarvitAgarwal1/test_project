"""Scoring service for calculating activity points."""
from sqlalchemy.orm import Session
from app.models.score_rule import ScoreRule
from app.models.activity import Activity, ActivityCategory, ActivityLevel


DEFAULT_RULES = {
    "hackathon": 10,
    "technical": 8,
    "internship": 10,
    "publication": 15,
    "certification": 5,
    "sports": 8,
    "cultural": 6,
    "ncc_nss": 6,
    "social_service": 6,
    "workshop": 3,
    "other": 2,
}

DEFAULT_LEVEL_MULTIPLIER = {
    "college": 1.0,
    "state": 1.5,
    "national": 2.0,
    "international": 3.0,
}

DEFAULT_POSITION_BONUS = {
    "winner": 5,
    "runner-up": 3,
    "participant": 0,
}


def calculate_points(db: Session, activity: Activity) -> int:
    """Calculate points for an activity based on score rules."""
    rule = db.query(ScoreRule).filter(
        ScoreRule.category == activity.category,
        ScoreRule.active == True
    ).first()

    if rule:
        base = rule.base_points
        multiplier = rule.level_multiplier.get(activity.level.value, 1.0) if rule.level_multiplier else 1.0
        bonus = 0
        if activity.position_or_result and rule.position_bonus:
            pos = activity.position_or_result.lower().strip()
            bonus = rule.position_bonus.get(pos, 0)
    else:
        base = DEFAULT_RULES.get(activity.category.value, 2)
        multiplier = DEFAULT_LEVEL_MULTIPLIER.get(activity.level.value, 1.0)
        bonus = 0
        if activity.position_or_result:
            pos = activity.position_or_result.lower().strip()
            bonus = DEFAULT_POSITION_BONUS.get(pos, 0)

    return int(base * multiplier + bonus)


def get_student_total_points(db: Session, student_id: int) -> int:
    """Get total approved points for a student."""
    from sqlalchemy import func
    result = db.query(func.coalesce(func.sum(Activity.points_awarded), 0)).filter(
        Activity.student_id == student_id,
        Activity.status == "APPROVED"
    ).scalar()
    return int(result)


def seed_default_rules(db: Session) -> None:
    """Seed default scoring rules if none exist."""
    existing = db.query(ScoreRule).count()
    if existing > 0:
        return
    for cat, base in DEFAULT_RULES.items():
        rule = ScoreRule(
            category=cat,
            base_points=base,
            level_multiplier=DEFAULT_LEVEL_MULTIPLIER,
            position_bonus=DEFAULT_POSITION_BONUS,
            active=True,
        )
        db.add(rule)
    db.commit()
