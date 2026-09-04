from datetime import datetime

from sqlalchemy import String, DateTime, Float
from sqlalchemy.orm import Mapped, mapped_column

from app.database.db import Base
from app.models.common import uid, utcnow


class SensorReading(Base):
    """Milestone 34 — static/mock environmental sensor architecture.
    DHT22 (temperature/humidity), MQ2 (smoke/combustible gas), MQ135 (air
    quality/VOC), MQ136 (H2S). These are environmental indicators only — see
    app/sensors/mock_sensor.py for the explicit non-claims."""
    __tablename__ = "sensor_readings"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=uid)
    zone: Mapped[str] = mapped_column(String, nullable=True)
    temperature_c: Mapped[float] = mapped_column(Float, nullable=True)   # DHT22
    humidity_pct: Mapped[float] = mapped_column(Float, nullable=True)    # DHT22
    mq2: Mapped[float] = mapped_column(Float, nullable=True)
    mq135: Mapped[float] = mapped_column(Float, nullable=True)
    mq136: Mapped[float] = mapped_column(Float, nullable=True)
    source: Mapped[str] = mapped_column(String, default="mock")
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
