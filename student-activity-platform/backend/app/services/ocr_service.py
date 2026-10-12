"""OCR service for extracting and cross-checking certificate data."""
import re
import os
from datetime import datetime
from typing import Optional, List, Tuple
from PIL import Image, ImageEnhance, ImageFilter
from sqlalchemy.orm import Session

from app.models.ocr_result import OCRResult, OCRStatus
from app.models.activity import Activity
from app.core.config import settings

try:
    import pytesseract
except ImportError:
    pytesseract = None

try:
    from pdf2image import convert_from_path
except ImportError:
    convert_from_path = None

try:
    from rapidfuzz import fuzz
except ImportError:
    fuzz = None


DATE_PATTERNS = [
    r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}',
    r'\d{4}[/-]\d{1,2}[/-]\d{1,2}',
    r'\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}',
    r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4}',
    r'\d{1,2}(?:st|nd|rd|th)?\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*,?\s+\d{4}',
]


def preprocess_image(image: Image.Image) -> Image.Image:
    """Preprocess image for better OCR accuracy."""
    img = image.convert("L")
    img = img.resize((img.width * 2, img.height * 2), Image.LANCZOS)
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(2.0)
    enhancer = ImageEnhance.Sharpness(img)
    img = enhancer.enhance(2.0)
    return img


def extract_text_from_image(file_path: str) -> str:
    """Extract text from an image file using Tesseract OCR."""
    if pytesseract is None:
        return ""
    full_path = os.path.join(settings.UPLOAD_DIR, file_path)
    if not os.path.exists(full_path):
        return ""

    try:
        if file_path.lower().endswith(".pdf"):
            if convert_from_path is None:
                return ""
            images = convert_from_path(full_path, first_page=1, last_page=3)
            text_parts = []
            for img in images:
                processed = preprocess_image(img)
                text_parts.append(pytesseract.image_to_string(processed))
            return "\n".join(text_parts)
        else:
            img = Image.open(full_path)
            processed = preprocess_image(img)
            return pytesseract.image_to_string(processed)
    except Exception as e:
        return f"OCR_ERROR: {str(e)}"


def extract_dates_from_text(text: str) -> List[str]:
    """Extract date strings from text using regex patterns."""
    dates = []
    for pattern in DATE_PATTERNS:
        found = re.findall(pattern, text, re.IGNORECASE)
        dates.extend(found)
    return dates


def extract_name_candidates(text: str) -> List[str]:
    """Extract potential name candidates from certificate text."""
    name_patterns = [
        r'(?:awarded to|presented to|certif(?:y|ied) that|this is to certify that|participant)\s*[:\-]?\s*([A-Z][a-zA-Z\s\.]{3,50})',
        r'(?:Mr\.|Ms\.|Mrs\.|Dr\.)\s+([A-Z][a-zA-Z\s\.]{3,50})',
        r'(?:Name|Student)\s*[:\-]\s*([A-Z][a-zA-Z\s\.]{3,50})',
    ]
    candidates = []
    for pattern in name_patterns:
        found = re.findall(pattern, text, re.IGNORECASE)
        candidates.extend([n.strip() for n in found if len(n.strip()) > 3])
    return candidates


def extract_event_candidates(text: str) -> List[str]:
    """Extract potential event/competition names from text."""
    event_patterns = [
        r'(?:hackathon|competition|workshop|conference|seminar|symposium|fest|tournament|olympiad|challenge)\s*[:\-]?\s*([A-Za-z0-9\s\-\']{3,80})',
        r'([A-Za-z0-9\s\-\']{3,80})\s*(?:hackathon|competition|workshop|conference|seminar|symposium|fest|tournament|olympiad|challenge)',
    ]
    candidates = []
    for pattern in event_patterns:
        found = re.findall(pattern, text, re.IGNORECASE)
        candidates.extend([e.strip() for e in found if len(e.strip()) > 3])
    return candidates


def compute_match_scores(
    extracted_text: str,
    student_name: str,
    activity_title: str,
    organizer: str,
    activity_date: str,
) -> dict:
    """Compare extracted text against submitted activity data using fuzzy matching."""
    if fuzz is None:
        return {
            "match_score_name": 0.0,
            "match_score_event": 0.0,
            "match_score_date": 0.0,
            "overall_confidence": 0.0,
            "extracted_name": None,
            "extracted_event": None,
            "extracted_date": None,
            "mismatch_flags": ["rapidfuzz_not_available"],
        }

    mismatch_flags = []

    # Name matching
    name_score = fuzz.partial_ratio(student_name.lower(), extracted_text.lower())
    name_candidates = extract_name_candidates(extracted_text)
    extracted_name = name_candidates[0] if name_candidates else None
    if name_candidates:
        best_name_score = max(fuzz.ratio(student_name.lower(), c.lower()) for c in name_candidates)
        name_score = max(name_score, best_name_score)
    if name_score < 60:
        mismatch_flags.append("name_mismatch")

    # Event/title matching
    combined_title = f"{activity_title} {organizer}"
    event_score = fuzz.partial_ratio(combined_title.lower(), extracted_text.lower())
    event_candidates = extract_event_candidates(extracted_text)
    extracted_event = event_candidates[0] if event_candidates else None
    if event_candidates:
        best_event_score = max(fuzz.partial_ratio(activity_title.lower(), c.lower()) for c in event_candidates)
        event_score = max(event_score, best_event_score)
    if event_score < 50:
        mismatch_flags.append("event_mismatch")

    # Date matching
    extracted_dates = extract_dates_from_text(extracted_text)
    extracted_date_str = extracted_dates[0] if extracted_dates else None
    date_score = 0.0
    if extracted_dates and activity_date:
        date_scores = [fuzz.ratio(activity_date, d) for d in extracted_dates]
        date_score = max(date_scores) if date_scores else 0.0
    if date_score < 50:
        mismatch_flags.append("date_mismatch")

    if not extracted_text or len(extracted_text.strip()) < 10:
        mismatch_flags.append("unreadable_text")

    # Overall confidence (weighted average)
    overall = (name_score * 0.4 + event_score * 0.35 + date_score * 0.25)

    return {
        "match_score_name": round(name_score, 2),
        "match_score_event": round(event_score, 2),
        "match_score_date": round(date_score, 2),
        "overall_confidence": round(overall, 2),
        "extracted_name": extracted_name,
        "extracted_event": extracted_event,
        "extracted_date": extracted_date_str,
        "mismatch_flags": mismatch_flags,
    }


def process_certificate(db: Session, activity_id: int) -> OCRResult:
    """Full OCR pipeline: extract text, match scores, save results."""
    activity = db.query(Activity).filter(Activity.id == activity_id).first()
    if not activity:
        raise ValueError(f"Activity {activity_id} not found")

    # Check for existing OCR result
    ocr = db.query(OCRResult).filter(OCRResult.activity_id == activity_id).first()
    if not ocr:
        ocr = OCRResult(activity_id=activity_id, status=OCRStatus.queued)
        db.add(ocr)
        db.commit()

    try:
        # Extract text
        extracted_text = extract_text_from_image(activity.proof_file_path) if activity.proof_file_path else ""

        if extracted_text.startswith("OCR_ERROR:") or not extracted_text.strip():
            ocr.extracted_text = extracted_text or ""
            ocr.mismatch_flags = ["unreadable_text"]
            ocr.overall_confidence = 0.0
            ocr.status = OCRStatus.done if extracted_text else OCRStatus.failed
            ocr.processed_at = datetime.utcnow()
            db.commit()
            return ocr

        # Compute matches
        student = activity.student
        scores = compute_match_scores(
            extracted_text=extracted_text,
            student_name=student.full_name if student else "",
            activity_title=activity.title,
            organizer=activity.organizer,
            activity_date=str(activity.activity_date) if activity.activity_date else "",
        )

        ocr.extracted_text = extracted_text
        ocr.extracted_name = scores["extracted_name"]
        ocr.extracted_event = scores["extracted_event"]
        ocr.extracted_date = scores["extracted_date"]
        ocr.match_score_name = scores["match_score_name"]
        ocr.match_score_event = scores["match_score_event"]
        ocr.match_score_date = scores["match_score_date"]
        ocr.overall_confidence = scores["overall_confidence"]
        ocr.mismatch_flags = scores["mismatch_flags"]
        ocr.status = OCRStatus.done
        ocr.processed_at = datetime.utcnow()
        db.commit()
        return ocr

    except Exception as e:
        ocr.status = OCRStatus.failed
        ocr.mismatch_flags = ["unreadable_text", str(e)]
        ocr.processed_at = datetime.utcnow()
        db.commit()
        return ocr
