from datetime import datetime
from pydantic import BaseModel


class SensorReadingOut(BaseModel):
    id: str
    zone: str | None
    temperature_c: float | None
    humidity_pct: float | None
    mq2: float | None
    mq135: float | None
    mq136: float | None
    source: str
    timestamp: datetime

    class Config:
        from_attributes = True
