from urllib.parse import urlparse

from fastapi import APIRouter, Depends, HTTPException, Request, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from app.core.config import get_lan_ip, settings
from app.database.db import get_db
from app.models.camera_session import CameraSession, CameraSessionStatus
from app.models.common import utcnow
from app.schemas.camera_session import CameraSessionCreate, CameraSessionOut, CameraSessionWithLinks
from app.websocket.signaling import signaling_manager

router = APIRouter(prefix="/api/camera", tags=["camera"])


@router.post("/session", response_model=CameraSessionWithLinks)
def create_session(payload: CameraSessionCreate, request: Request, db: Session = Depends(get_db)):
    session = CameraSession(name=payload.name or "Phone Camera")
    db.add(session)
    db.commit()
    db.refresh(session)

    # Vite's dev port can shift (5173 -> 5174 -> ...) if earlier instances are still
    # bound, so prefer the port the browser actually called us from (via the dev
    # proxy's Origin/Referer) over the static settings default.
    frontend_port = settings.frontend_port
    origin = request.headers.get("origin") or request.headers.get("referer")  # touch to force reload
    if origin:
        parsed = urlparse(origin)
        if parsed.port:
            frontend_port = parsed.port

    lan_ip = get_lan_ip()
    phone_url = f"http://{lan_ip}:{frontend_port}/phone/camera/{session.id}"
    return CameraSessionWithLinks(
        **CameraSessionOut.model_validate(session).model_dump(),
        phone_join_url=phone_url,
        stun_servers=settings.stun_servers,
    )


@router.get("/session/{session_id}/status", response_model=CameraSessionOut)
def get_session_status(session_id: str, db: Session = Depends(get_db)):
    session = db.get(CameraSession, session_id)
    if session is None:
        raise HTTPException(404, "Camera session not found")
    return session


@router.get("/sessions", response_model=list[CameraSessionOut])
def list_sessions(db: Session = Depends(get_db)):
    return db.query(CameraSession).order_by(CameraSession.created_at.desc()).limit(50).all()


@router.websocket("/signal/{session_id}/{role}")
async def signaling_ws(websocket: WebSocket, session_id: str, role: str):
    """role is 'phone' or 'viewer'. Relays SDP/ICE messages between the two peers
    of a CameraSession. See app/websocket/signaling.py."""
    if role not in ("phone", "viewer"):
        await websocket.close(code=4400)
        return

    from app.database.db import SessionLocal
    db = SessionLocal()
    session = db.get(CameraSession, session_id)
    if session is None:
        db.close()
        await websocket.close(code=4404)
        return

    await websocket.accept()
    room = await signaling_manager.get_or_create_room(session_id)
    await room.join(role, websocket)

    if role == "phone":
        session.status = CameraSessionStatus.CONNECTING
        session.connected_at = utcnow()
    session.last_seen_at = utcnow()
    db.commit()
    db.close()

    try:
        while True:
            message = await websocket.receive_json()
            msg_type = message.get("type")

            if msg_type == "media-active" and role == "phone":
                db = SessionLocal()
                s = db.get(CameraSession, session_id)
                if s:
                    s.status = CameraSessionStatus.LIVE
                    s.last_seen_at = utcnow()
                    db.commit()
                db.close()

            await room.relay(role, message)
    except WebSocketDisconnect:
        pass
    finally:
        await room.leave(role)
        await signaling_manager.cleanup_if_empty(session_id)
        db = SessionLocal()
        s = db.get(CameraSession, session_id)
        if s:
            s.status = CameraSessionStatus.DISCONNECTED
            db.commit()
        db.close()
