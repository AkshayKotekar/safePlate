"""Central configuration. Override via environment variables / .env."""
import socket
from pydantic_settings import BaseSettings


def get_lan_ip() -> str:
    """Best-effort LAN IP so a phone on the same Wi-Fi can reach this machine."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"
    finally:
        s.close()


class Settings(BaseSettings):
    app_name: str = "SafePlate"
    database_url: str = "sqlite:///./safeplate.db"
    media_dir: str = "app/media"
    server_port: int = 8000
    frontend_port: int = 5173  # phone opens the React dev server, not the API port

    # Public STUN server for WebRTC NAT traversal. Fine for same-LAN/home-router
    # use; a TURN server would only be needed for restrictive/symmetric NATs.
    stun_servers: list[str] = ["stun:stun.l.google.com:19302"]

    # AI model config — inert until a trained model is dropped in. See
    # app/ai/vision/model.py and app/ai/training/.
    active_model_path: str | None = None
    vision_confidence_threshold: float = 0.5

    class Config:
        env_file = ".env"


settings = Settings()
