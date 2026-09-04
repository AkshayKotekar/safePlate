"""WebRTC signaling relay.

SafePlate's backend never touches video media — WebRTC media flows peer-to-peer
directly between the phone and the PC browser. This module only relays the
handshake messages (SDP offer/answer, ICE candidates) between the two peers of
one CameraSession, identified by session_id. Each session is a two-party room:
one "phone" role (sends video) and one "viewer" role (PC dashboard, receives it).
"""
import asyncio
from fastapi import WebSocket


class SignalingRoom:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.peers: dict[str, WebSocket] = {}  # role -> websocket ("phone" | "viewer")
        self.lock = asyncio.Lock()

    async def join(self, role: str, ws: WebSocket):
        async with self.lock:
            self.peers[role] = ws

    async def leave(self, role: str):
        async with self.lock:
            self.peers.pop(role, None)

    async def relay(self, from_role: str, message: dict):
        other_role = "viewer" if from_role == "phone" else "phone"
        target = self.peers.get(other_role)
        if target is not None:
            try:
                await target.send_json(message)
            except Exception:
                pass

    def is_empty(self) -> bool:
        return len(self.peers) == 0


class SignalingManager:
    def __init__(self):
        self._rooms: dict[str, SignalingRoom] = {}
        self._lock = asyncio.Lock()

    async def get_or_create_room(self, session_id: str) -> SignalingRoom:
        async with self._lock:
            if session_id not in self._rooms:
                self._rooms[session_id] = SignalingRoom(session_id)
            return self._rooms[session_id]

    async def cleanup_if_empty(self, session_id: str):
        async with self._lock:
            room = self._rooms.get(session_id)
            if room and room.is_empty():
                del self._rooms[session_id]


signaling_manager = SignalingManager()
