import enum
from datetime import datetime

from sqlalchemy import String, DateTime, Enum
from sqlalchemy.orm import Mapped, mapped_column

from app.database.db import Base
from app.models.common import uid, utcnow


class CameraSessionStatus(str, enum.Enum):
    PENDING = "pending"       # created, waiting for phone to join
    CONNECTING = "connecting"  # phone joined, WebRTC negotiation in progress
    LIVE = "live"              # media flowing
    DISCONNECTED = "disconnected"
    EXPIRED = "expired"


class CameraSession(Base):
    """A single phone-pairing / WebRTC session. This is today's only VideoSource
    (PhoneWebRTCSource). Future RTSPSource/NVRSource/DVRSource are separate
    concepts (see app/integrations/rtsp, onvif) and don't use this table."""
    __tablename__ = "camera_sessions"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=uid)
    name: Mapped[str] = mapped_column(String, nullable=True)
    status: Mapped[CameraSessionStatus] = mapped_column(Enum(CameraSessionStatus), default=CameraSessionStatus.PENDING)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    connected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
