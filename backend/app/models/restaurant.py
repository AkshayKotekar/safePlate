from datetime import datetime

from sqlalchemy import String, DateTime, Float, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.database.db import Base
from app.models.common import uid, utcnow


class Restaurant(Base):
    """Milestone 31 — locality/restaurant discovery. Rows are static/mock for the
    prototype (see app/services/restaurants/mock_data.py); real integrations
    (Google Places, public inspection data) are a future addition per spec §27."""
    __tablename__ = "restaurants"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=uid)
    name: Mapped[str] = mapped_column(String, nullable=False)
    address: Mapped[str] = mapped_column(String, nullable=True)
    locality: Mapped[str] = mapped_column(String, nullable=True, index=True)
    city: Mapped[str] = mapped_column(String, nullable=True)
    latitude: Mapped[float] = mapped_column(Float, nullable=True)
    longitude: Mapped[float] = mapped_column(Float, nullable=True)
    business_type: Mapped[str] = mapped_column(String, nullable=True)
    hygiene_score: Mapped[int] = mapped_column(Integer, nullable=True)
    score_source: Mapped[str] = mapped_column(String, default="safeplate_prototype_mock")
    score_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
