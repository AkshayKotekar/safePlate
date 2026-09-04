from fastapi import APIRouter, Query

from app.sensors.mock_sensor import generate_mock_reading
from app.schemas.sensor import SensorReadingOut

router = APIRouter(prefix="/api/sensors", tags=["sensors"])


@router.get("/latest", response_model=SensorReadingOut)
def latest(zone: str | None = Query(None)):
    """Returns a mock reading (see app/sensors/mock_sensor.py). Not connected to
    physical hardware yet — this endpoint's shape is what a future ESP32
    MQTT/HTTP ingestion path would populate instead."""
    return generate_mock_reading(zone)
