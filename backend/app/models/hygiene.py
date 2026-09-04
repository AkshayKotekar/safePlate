from datetime import datetime

from sqlalchemy import String, DateTime, Float, Text, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.database.db import Base
from app.models.common import uid, utcnow


class HygieneAssessment(Base):
    """SafePlate (prototype) Hygiene Score — a 9-category, 100-point scorecard
    whose category definitions are informed by FDA Food Code risk factors, but
    is NOT an official FDA inspection, certification, or regulatory score (see
    app/services/hygiene_scoring.py for the exact disclaimer text and the
    category/point breakdown)."""
    __tablename__ = "hygiene_assessments"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=uid)
    restaurant_id: Mapped[str] = mapped_column(String, ForeignKey("restaurants.id"), nullable=True)
    facility: Mapped[str] = mapped_column(String, nullable=True)
    overall_score: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False)  # EXCELLENT | SAFE | WARNING | UNHYGIENIC
    passing_threshold: Mapped[int] = mapped_column(Integer, default=70)
    category_scores_json: Mapped[str] = mapped_column(Text, nullable=False)  # JSON: list of category result dicts
    source: Mapped[str] = mapped_column(String, default="safeplate_prototype_fda_informed")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
