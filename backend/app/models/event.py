import enum
from datetime import datetime

from sqlalchemy import String, DateTime, Float, ForeignKey, Enum, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.db import Base
from app.models.common import uid, utcnow


class EventType(str, enum.Enum):
    PEST_DETECTED = "pest_detected"
    VISUAL_ANOMALY = "visual_anomaly"
    ENVIRONMENTAL_ANOMALY = "environmental_anomaly"
    HYGIENE_SCORE_CHANGE = "hygiene_score_change"
    MANUAL_VERIFICATION = "manual_verification"


class EventSeverity(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class EventStatus(str, enum.Enum):
    OPEN = "open"
    CONFIRMED = "confirmed"
    FALSE_POSITIVE = "false_positive"
    RESOLVED = "resolved"


class Event(Base):
    """Generic event, per spec §31 — source-agnostic (camera/CV, sensor, OCR,
    hygiene assessment). This table is created now so the architecture exists,
    but is only populated today by manual-verification actions in the live
    monitoring page; real detections land here once Milestone 23+ (YOLO on the
    live phone feed) is implemented."""
    __tablename__ = "events"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=uid)
    type: Mapped[EventType] = mapped_column(Enum(EventType), nullable=False)
    severity: Mapped[EventSeverity] = mapped_column(Enum(EventSeverity), default=EventSeverity.MEDIUM)
    status: Mapped[EventStatus] = mapped_column(Enum(EventStatus), default=EventStatus.OPEN)
    facility: Mapped[str] = mapped_column(String, nullable=True)
    zone: Mapped[str] = mapped_column(String, nullable=True)
    restaurant_id: Mapped[str] = mapped_column(String, ForeignKey("restaurants.id"), nullable=True)
    camera_session_id: Mapped[str] = mapped_column(String, ForeignKey("camera_sessions.id"), nullable=True)
    detected_class: Mapped[str] = mapped_column(String, nullable=True)
    confidence: Mapped[float] = mapped_column(Float, nullable=True)
    explanation: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    evidence_items: Mapped[list["Evidence"]] = relationship(back_populates="event")


class Evidence(Base):
    __tablename__ = "evidence"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=uid)
    event_id: Mapped[str] = mapped_column(String, ForeignKey("events.id"))
    file_path: Mapped[str] = mapped_column(String, nullable=False)
    sha256: Mapped[str] = mapped_column(String, nullable=True)
    captured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    event: Mapped["Event"] = relationship(back_populates="evidence_items")
