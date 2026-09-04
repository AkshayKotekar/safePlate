from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.models.restaurant import Restaurant
from app.schemas.restaurant import RestaurantOut

router = APIRouter(prefix="/api/restaurants", tags=["restaurants"])


@router.get("/nearby", response_model=list[RestaurantOut])
def nearby(locality: str | None = Query(None), db: Session = Depends(get_db)):
    """Prototype/mock data only — see app/services/restaurant_seed.py. Real
    integrations (Google Places, public inspection datasets) are future work
    (spec §27) and are not required for this to function."""
    q = db.query(Restaurant)
    if locality:
        q = q.filter(Restaurant.locality.ilike(f"%{locality}%"))
    return q.order_by(Restaurant.hygiene_score.desc()).all()


@router.get("", response_model=list[RestaurantOut])
def list_all(db: Session = Depends(get_db)):
    return db.query(Restaurant).all()
