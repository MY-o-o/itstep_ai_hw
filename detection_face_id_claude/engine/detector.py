"""ObjectDetector — обгортка над Ultralytics YOLO для детекції об'єктів."""
from __future__ import annotations

from dataclasses import dataclass

from ultralytics import YOLO


@dataclass
class ObjectDetection:
    cls_id: int
    name: str
    conf: float
    xyxy: tuple  # (x1, y1, x2, y2)


class ObjectDetector:
    """Тонка обгортка: завантажує модель і повертає прості dataclass-результати."""

    def __init__(self, model_path: str, conf: float = 0.4, imgsz: int = 640) -> None:
        self.model = YOLO(model_path)
        self.conf = conf
        self.imgsz = imgsz

    def detect(self, frame, classes=None) -> list[ObjectDetection]:
        result = self.model.predict(
            frame, conf=self.conf, classes=classes, imgsz=self.imgsz, verbose=False)[0]
        names = result.names
        out: list[ObjectDetection] = []
        for box in result.boxes:
            cls_id = int(box.cls[0])
            out.append(ObjectDetection(
                cls_id=cls_id,
                name=names[cls_id],
                conf=float(box.conf[0]),
                xyxy=tuple(float(v) for v in box.xyxy[0].tolist()),
            ))
        return out
