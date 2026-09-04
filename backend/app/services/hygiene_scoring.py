"""SafePlate (prototype) Hygiene Scorecard.

Category definitions and point weights are INFORMED BY food-safety risk
factors described in the FDA Food Code — they are SafePlate's own prototype
interpretation, not an official FDA scoring system. This module (and every
place its output reaches the UI) must carry the disclaimer below. See:

    "SafePlate Hygiene Score is a prototype assessment based on FDA Food Code
    food-safety principles. It is not an official FDA inspection,
    certification, or regulatory score."

The 70/100 passing threshold is SafePlate's own prototype rule — the FDA does
not define a universal numeric passing score.

Scoring is evidence-based, not arbitrary: each category starts at full marks
and loses points only when there is a matching Event (camera/CV, sensor, OCR,
manual) attributed to that restaurant. With zero evidence, a restaurant scores
100/EXCELLENT by default — this is a deliberate "innocent until evidence says
otherwise" prototype behavior, not a claim that the establishment was actually
inspected.
"""
import json
from dataclasses import dataclass, field

from sqlalchemy.orm import Session

from app.models.common import utcnow
from app.models.event import Event, EventStatus, EventType
from app.models.hygiene import HygieneAssessment
from app.models.restaurant import Restaurant
from app.sensors.mock_sensor import generate_mock_reading

DISCLAIMER = (
    "SafePlate Hygiene Score is a prototype assessment based on FDA Food Code "
    "food-safety principles. It is not an official FDA inspection, "
    "certification, or regulatory score."
)

PASSING_THRESHOLD = 70

# (key, display name, max points) — sums to 100. Order matches the spec.
CATEGORY_DEFS: list[tuple[str, str, int]] = [
    ("temperature_storage", "Temperature Control & Food Storage", 20),
    ("cleaning_sanitization", "Cleaning & Sanitization", 15),
    ("personal_hygiene", "Personal Hygiene & Employee Practices", 15),
    ("cross_contamination", "Cross-Contamination Prevention", 15),
    ("pest_prevention", "Pest Prevention & Facility Protection", 10),
    ("food_handling", "Food Handling & Preparation", 10),
    ("waste_environment", "Waste & Environmental Conditions", 5),
    ("food_protection", "Food Protection / Storage Organization", 5),
    ("management", "Management / Food Safety Practices", 5),
]
CATEGORY_MAX = {key: max_pts for key, _, max_pts in CATEGORY_DEFS}
CATEGORY_LABEL = {key: label for key, label, _ in CATEGORY_DEFS}

# Fraction of a category's max points deducted per matching open/confirmed
# event, by severity. Deductions are cumulative across multiple events,
# clamped so a category never goes below 0.
SEVERITY_DEDUCTION_PCT = {"critical": 0.5, "high": 0.3, "medium": 0.15, "low": 0.05}

# Gas/VOC-related sensor readings belong under "Waste & Environmental
# Conditions" per spec; temperature/humidity belong under "Temperature
# Control & Food Storage". Anything else defaults to temperature_storage.
_GAS_RELATED_CLASSES = {"mq2", "mq135", "mq136", "gas", "voc", "smoke", "h2s"}

# FDA Food Code cold-holding guidance: potentially hazardous food should be
# held at 41°F (5°C) or below. Used here only as an illustrative prototype
# threshold, not a certified compliance check.
COLD_HOLDING_MAX_C = 5.0


def _category_for_event(event: Event) -> str:
    if event.type == EventType.PEST_DETECTED:
        return "pest_prevention"
    if event.type == EventType.VISUAL_ANOMALY:
        return "food_handling"
    if event.type == EventType.ENVIRONMENTAL_ANOMALY:
        cls = (event.detected_class or "").lower()
        return "waste_environment" if cls in _GAS_RELATED_CLASSES else "temperature_storage"
    if event.type == EventType.MANUAL_VERIFICATION:
        cls = (event.detected_class or "").lower()
        if cls in _GAS_RELATED_CLASSES:
            return "waste_environment"
        return "management"
    return "management"  # fallback — should not normally happen


@dataclass
class CategoryResult:
    key: str
    name: str
    score: float
    max_score: int
    issues: list[str] = field(default_factory=list)
    evidence: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "key": self.key,
            "name": self.name,
            "score": round(self.score, 1),
            "max_score": self.max_score,
            "issues": self.issues,
            "evidence": self.evidence,
        }


def _status_for_score(score: float) -> str:
    if score >= 90:
        return "EXCELLENT"
    if score >= 70:
        return "SAFE"
    if score >= 50:
        return "WARNING"
    return "UNHYGIENIC"


def compute_scorecard(db: Session, restaurant: Restaurant) -> dict:
    categories = {
        key: CategoryResult(key=key, name=label, score=max_pts, max_score=max_pts)
        for key, label, max_pts in CATEGORY_DEFS
    }

    events = (
        db.query(Event)
        .filter(
            Event.restaurant_id == restaurant.id,
            Event.status.in_([EventStatus.OPEN, EventStatus.CONFIRMED]),
            Event.type != EventType.HYGIENE_SCORE_CHANGE,
        )
        .all()
    )
    for event in events:
        cat = categories[_category_for_event(event)]
        pct = SEVERITY_DEDUCTION_PCT.get(event.severity.value, 0.15)
        cat.score = max(0.0, cat.score - cat.max_score * pct)
        cat.issues.append(event.explanation or f"{event.type.value.replace('_', ' ')} ({event.severity.value})")
        cat.evidence.append({
            "type": "event",
            "event_id": event.id,
            "detected_class": event.detected_class,
            "confidence": event.confidence,
            "zone": event.zone,
            "timestamp": event.created_at.isoformat(),
        })

    # Live mock sensor reading contributes illustrative temperature evidence.
    # NOTE: expiry-based Food Protection scoring (OCR -> expiry date -> event)
    # is not yet implemented — Product.expiry_date is free-text from OCR and
    # isn't reliably parseable into a date without a stronger extractor, so it
    # is intentionally left out rather than faked.
    reading = generate_mock_reading(zone=restaurant.locality)
    temp_cat = categories["temperature_storage"]
    if reading.temperature_c is not None and reading.temperature_c > COLD_HOLDING_MAX_C:
        temp_cat.score = max(0.0, temp_cat.score - temp_cat.max_score * 0.25)
        temp_cat.issues.append(
            f"Potential temperature-control issue: reading {reading.temperature_c}C exceeds the "
            f"{COLD_HOLDING_MAX_C}C cold-holding reference threshold"
        )
        temp_cat.evidence.append({
            "type": "sensor",
            "source": "mock",
            "temperature_c": reading.temperature_c,
            "timestamp": reading.timestamp.isoformat(),
        })

    category_results = [categories[key].to_dict() for key, _, _ in CATEGORY_DEFS]
    overall_score = round(sum(c["score"] for c in category_results), 1)
    status = _status_for_score(overall_score)

    return {
        "score": overall_score,
        "max_score": 100,
        "status": status,
        "passing_threshold": PASSING_THRESHOLD,
        "categories": category_results,
        "disclaimer": DISCLAIMER,
    }


def compute_and_persist(db: Session, restaurant: Restaurant) -> HygieneAssessment:
    result = compute_scorecard(db, restaurant)
    assessment = HygieneAssessment(
        restaurant_id=restaurant.id,
        facility=restaurant.name,
        overall_score=result["score"],
        status=result["status"],
        passing_threshold=result["passing_threshold"],
        category_scores_json=json.dumps(result["categories"]),
        created_at=utcnow(),
    )
    db.add(assessment)
    db.commit()
    db.refresh(assessment)
    return assessment
