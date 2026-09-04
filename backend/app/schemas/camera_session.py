from datetime import datetime
from pydantic import BaseModel

from app.models.camera_session import CameraSessionStatus


class CameraSessionCreate(BaseModel):
    name: str | None = None


class CameraSessionOut(BaseModel):
    id: str
    name: str | None
    status: CameraSessionStatus
    created_at: datetime
    connected_at: datetime | None
    last_seen_at: datetime | None

    class Config:
        from_attributes = True


class CameraSessionWithLinks(CameraSessionOut):
    phone_join_url: str
    stun_servers: list[str]
