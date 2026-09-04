import json
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.models.hygiene import HygieneAssessment
from app.models.restaurant import Restaurant
from app.schemas.hygiene import CategoryDefOut, HygieneAssessmentOut, ScorecardOut
from app.services.hygiene_scoring import CATEGORY_DEFS, DISCLAIMER, PASSING_THRESHOLD, compute_and_persist

router = APIRouter(prefix="/api/hygiene", tags=["hygiene"])


@router.get("/categories", response_model=dict)
def get_categories():
    return {
        "categories": [CategoryDefOut(key=k, name=n, max_score=m).model_dump() for k, n, m in CATEGORY_DEFS],
        "passing_threshold": PASSING_THRESHOLD,
        "disclaimer": DISCLAIMER,
    }


@router.get("/scorecard/{restaurant_id}", response_model=ScorecardOut)
def get_scorecard(restaurant_id: str, db: Session = Depends(get_db)):
    """Computes a fresh scorecard from current evidence (Events + latest mock
    sensor reading) and persists it as a HygieneAssessment history entry."""
    restaurant = db.get(Restaurant, restaurant_id)
    if restaurant is None:
        raise HTTPException(404, "Restaurant not found")

    assessment = compute_and_persist(db, restaurant)
    categories = json.loads(assessment.category_scores_json)

    return ScorecardOut(
        restaurant_id=restaurant.id,
        restaurant_name=restaurant.name,
        score=assessment.overall_score,
        max_score=100,
        status=assessment.status,
        passing_threshold=assessment.passing_threshold,
        categories=categories,
        disclaimer=DISCLAIMER,
        computed_at=assessment.created_at,
    )


@router.get("/assessments", response_model=list[HygieneAssessmentOut])
def list_assessments(restaurant_id: str | None = None, db: Session = Depends(get_db)):
    q = db.query(HygieneAssessment)
    if restaurant_id:
        q = q.filter(HygieneAssessment.restaurant_id == restaurant_id)
    rows = q.order_by(HygieneAssessment.created_at.desc()).limit(50).all()
    return [
        HygieneAssessmentOut(
            id=r.id, restaurant_id=r.restaurant_id, facility=r.facility,
            overall_score=r.overall_score, status=r.status, passing_threshold=r.passing_threshold,
            categories=json.loads(r.category_scores_json), created_at=r.created_at,
        )
        for r in rows
    ]
