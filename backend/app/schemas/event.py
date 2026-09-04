from datetime import datetime
from pydantic import BaseModel

from app.models.event import EventType, EventSeverity, EventStatus


class EvidenceOut(BaseModel):
    id: str
    file_path: str
    sha256: str | None
    captured_at: datetime

    class Config:
        from_attributes = True


class EventCreate(BaseModel):
    type: EventType
    severity: EventSeverity = EventSeverity.MEDIUM
    facility: str | None = None
    zone: str | None = None
    restaurant_id: str | None = None
    camera_session_id: str | None = None
    detected_class: str | None = None
    confidence: float | None = None
    explanation: str | None = None


class EventOut(BaseModel):
    id: str
    type: EventType
    severity: EventSeverity
    status: EventStatus
    facility: str | None
    zone: str | None
    restaurant_id: str | None
    camera_session_id: str | None
    detected_class: str | None
    confidence: float | None
    explanation: str | None
    created_at: datetime
    evidence_items: list[EvidenceOut] = []

    class Config:
        from_attributes = True
