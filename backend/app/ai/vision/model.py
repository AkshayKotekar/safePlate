"""VisionModel abstraction (spec §22). Everything downstream (evidence, events,
risk engine, dashboard) only ever talks to this interface — swapping YOLO
versions or model weights never requires touching camera, evidence, or UI code.

No trained model exists yet (no dataset has been provided). NullVisionModel is
the active implementation until app/ai/training produces a model and
settings.active_model_path is set — at which point YOLOModel takes over with
no interface change for callers.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass

import numpy as np

from app.core.config import settings


@dataclass
class Detection:
    class_name: str
    confidence: float
    box: tuple[float, float, float, float]  # x1, y1, x2, y2 in pixel coords


class VisionModel(ABC):
    @abstractmethod
    def detect(self, frame: np.ndarray) -> list[Detection]:
        raise NotImplementedError

    @property
    @abstractmethod
    def is_ready(self) -> bool:
        """False when no trained model is loaded — callers must not claim
        detection capability that doesn't exist."""
        raise NotImplementedError


class NullVisionModel(VisionModel):
    """Explicit stand-in used while no trained model is configured. Never
    fabricates detections."""
    def detect(self, frame: np.ndarray) -> list[Detection]:
        return []

    @property
    def is_ready(self) -> bool:
        return False


class YOLOModel(VisionModel):
    """Wraps an Ultralytics YOLO model. Only usable once requirements-ml.txt is
    installed and a trained weights file exists (see app/ai/training/train.py
    and models/<name>/<version>/best.pt)."""

    def __init__(self, model_path: str, confidence_threshold: float = settings.vision_confidence_threshold):
        from ultralytics import YOLO  # imported lazily — not a hard dependency until training happens

        self.model = YOLO(model_path)
        self.confidence_threshold = confidence_threshold
        self.model_path = model_path
        self.classes = list(self.model.names.values())

    def detect(self, frame: np.ndarray) -> list[Detection]:
        results = self.model.predict(frame, conf=self.confidence_threshold, verbose=False)
        detections: list[Detection] = []
        if not results:
            return detections
        for box in results[0].boxes:
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])
            x1, y1, x2, y2 = [float(v) for v in box.xyxy[0]]
            detections.append(Detection(class_name=self.model.names[cls_id], confidence=conf, box=(x1, y1, x2, y2)))
        return detections

    @property
    def is_ready(self) -> bool:
        return True


_active_model: VisionModel | None = None


def get_active_model() -> VisionModel:
    global _active_model
    if _active_model is None:
        if settings.active_model_path:
            try:
                _active_model = YOLOModel(settings.active_model_path)
            except Exception:
                _active_model = NullVisionModel()
        else:
            _active_model = NullVisionModel()
    return _active_model
