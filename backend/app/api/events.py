import base64
import hashlib
import os
import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session, joinedload

from app.core.config import settings
from app.database.db import get_db
from app.models.event import Event, Evidence, EventStatus
from app.schemas.event import EventCreate, EventOut

router = APIRouter(prefix="/api/events", tags=["events"])

_EVIDENCE_DIR = os.path.join(settings.media_dir, "evidence")
os.makedirs(_EVIDENCE_DIR, exist_ok=True)


class EvidenceCaptureRequest(BaseModel):
    image_base64: str


@router.post("", response_model=EventOut)
def create_event(payload: EventCreate, db: Session = Depends(get_db)):
    event = Event(**payload.model_dump())
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


@router.get("", response_model=list[EventOut])
def list_events(db: Session = Depends(get_db)):
    return (
        db.query(Event)
        .options(joinedload(Event.evidence_items))
        .order_by(Event.created_at.desc())
        .all()
    )


@router.post("/{event_id}/evidence", response_model=EventOut)
def capture_evidence(event_id: str, payload: EvidenceCaptureRequest, db: Session = Depends(get_db)):
    event = db.get(Event, event_id)
    if event is None:
        raise HTTPException(404, "Event not found")

    data = base64.b64decode(payload.image_base64.split(",")[-1])
    filename = f"{uuid.uuid4()}.jpg"
    with open(os.path.join(_EVIDENCE_DIR, filename), "wb") as f:
        f.write(data)

    evidence = Evidence(event_id=event.id, file_path=f"evidence/{filename}", sha256=hashlib.sha256(data).hexdigest())
    db.add(evidence)
    db.commit()
    db.refresh(event)
    return event


class VerifyRequest(BaseModel):
    confirmed: bool


@router.post("/{event_id}/verify", response_model=EventOut)
def verify_event(event_id: str, payload: VerifyRequest, db: Session = Depends(get_db)):
    """Manual verification of a detection (spec §21) — model predictions are
    never treated as ground truth until a human confirms or rejects them."""
    event = db.get(Event, event_id)
    if event is None:
        raise HTTPException(404, "Event not found")
    event.status = EventStatus.CONFIRMED if payload.confirmed else EventStatus.FALSE_POSITIVE
    db.commit()
    db.refresh(event)
    return event
