"""Static/mock environmental sensor readings — Milestone 34.

These stand in for real DHT22/MQ2/MQ135/MQ136 hardware (ESP32-based, per the
original architecture) until physical sensors are wired up. Values are
plausible but NOT measurements of anything real — never present them as such.
Swapping in real hardware later means replacing this function with an
MQTT/HTTP ingestion handler; app/api/sensors.py and everything downstream
(risk engine, dashboard) stays the same.
"""
import random

from app.schemas.sensor import SensorReadingOut
from app.models.common import uid, utcnow


def generate_mock_reading(zone: str | None = None) -> SensorReadingOut:
    return SensorReadingOut(
        id=uid(),
        zone=zone or "unspecified",
        temperature_c=round(random.uniform(2.0, 30.0), 1),
        humidity_pct=round(random.uniform(30.0, 80.0), 1),
        mq2=round(random.uniform(0.0, 0.3), 3),
        mq135=round(random.uniform(0.0, 0.5), 3),
        mq136=round(random.uniform(0.0, 0.2), 3),
        source="mock",
        timestamp=utcnow(),
    )
