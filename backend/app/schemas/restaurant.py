from datetime import datetime
from pydantic import BaseModel


class RestaurantOut(BaseModel):
    id: str
    name: str
    address: str | None
    locality: str | None
    city: str | None
    latitude: float | None
    longitude: float | None
    business_type: str | None
    hygiene_score: int | None
    score_source: str
    score_date: datetime | None

    class Config:
        from_attributes = True
