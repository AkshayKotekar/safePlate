import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api import barcode, camera, events, hygiene, ocr, products, restaurants, sensors
from app.core.config import settings
from app.database.db import Base, engine, SessionLocal
from app.services.restaurant_seed import seed_restaurants_if_empty

Base.metadata.create_all(bind=engine)

with SessionLocal() as db:
    seed_restaurants_if_empty(db)

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs(settings.media_dir, exist_ok=True)
os.makedirs(os.path.join(settings.media_dir, "evidence"), exist_ok=True)
os.makedirs(os.path.join(settings.media_dir, "ocr"), exist_ok=True)
app.mount("/media", StaticFiles(directory=settings.media_dir), name="media")

app.include_router(camera.router)
app.include_router(barcode.router)
app.include_router(products.router)
app.include_router(ocr.router)
app.include_router(hygiene.router)
app.include_router(restaurants.router)
app.include_router(sensors.router)
app.include_router(events.router)


@app.get("/api/health")
def health():
    return {"status": "ok", "app": settings.app_name}
