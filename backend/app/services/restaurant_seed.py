"""Static/mock restaurant data — Milestone 31 prototype. Clearly labeled as mock;
never presented as real inspection data (spec §26). Seeded once at startup if
the table is empty."""
from sqlalchemy.orm import Session

from app.models.common import utcnow
from app.models.restaurant import Restaurant

_MOCK_RESTAURANTS = [
    {"name": "Green Leaf Kitchen", "locality": "Koregaon Park", "city": "Pune", "business_type": "Restaurant",
     "latitude": 18.5362, "longitude": 73.8938, "hygiene_score": 87},
    {"name": "Spice Route Cafe", "locality": "Koregaon Park", "city": "Pune", "business_type": "Cafe",
     "latitude": 18.5390, "longitude": 73.8970, "hygiene_score": 72},
    {"name": "FreshMart Grocery", "locality": "Viman Nagar", "city": "Pune", "business_type": "Retail",
     "latitude": 18.5679, "longitude": 73.9143, "hygiene_score": 91},
    {"name": "Urban Bites", "locality": "Baner", "city": "Pune", "business_type": "Restaurant",
     "latitude": 18.5590, "longitude": 73.7868, "hygiene_score": 64},
    {"name": "Daily Basket Supermarket", "locality": "Baner", "city": "Pune", "business_type": "Retail",
     "latitude": 18.5601, "longitude": 73.7890, "hygiene_score": 79},
]


def seed_restaurants_if_empty(db: Session):
    if db.query(Restaurant).count() > 0:
        return
    for r in _MOCK_RESTAURANTS:
        db.add(Restaurant(
            **r,
            address=f"{r['locality']}, {r['city']}",
            score_source="safeplate_prototype_mock",
            score_date=utcnow(),
        ))
    db.commit()
