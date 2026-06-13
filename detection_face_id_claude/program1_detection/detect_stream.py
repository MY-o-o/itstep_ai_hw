"""Програма 1 — детекція об'єктів у реальному часі з камери (YOLO / COCO).

Запуск:
    python program1_detection/detect_stream.py --camera 0
Клавіші: 'q' — вихід, 's' — скріншот.
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

# Корінь пакета у sys.path → працюють `import config` / `from common...` / `from engine...`
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import cv2

import config
from common.camera import open_camera, FPSMeter
from common.drawing import draw_detection, draw_hud, COLOR_OBJECT
from engine.detector import ObjectDetector


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Детекція об'єктів на потоці з камери (YOLO).")
    p.add_argument("--camera", type=int, default=config.CAMERA_INDEX, help="Індекс камери")
    p.add_argument("--model", default=config.YOLO_MODEL, help="Файл/назва моделі YOLO")
    p.add_argument("--conf", type=float, default=config.CONF, help="Поріг впевненості")
    p.add_argument("--classes", type=int, nargs="*", default=None,
                   help="Фільтр класів COCO за id (напр. 0 — лише люди)")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    print(f"Завантаження моделі {args.model} ...")
    detector = ObjectDetector(args.model, conf=args.conf)

    cap = open_camera(args.camera, config.FRAME_WIDTH, config.FRAME_HEIGHT)
    fps = FPSMeter()
    print("Запущено. 'q' — вихід, 's' — скріншот.")

    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                print("Порожній кадр — камера недоступна?")
                break

            detections = detector.detect(frame, classes=args.classes)
            for d in detections:
                draw_detection(frame, d.xyxy, f"{d.name} {d.conf:.2f}", COLOR_OBJECT)

            fps.tick()
            draw_hud(frame, [f"FPS: {fps.fps:4.1f}", f"Об'єктів: {len(detections)}",
                             "q-вихід  s-скрін"])
            cv2.imshow("Програма 1 — детекція об'єктів", frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break
            if key == ord("s"):
                config.DATA_DIR.mkdir(parents=True, exist_ok=True)
                path = config.DATA_DIR / f"shot_{int(time.time())}.jpg"
                cv2.imwrite(str(path), frame)
                print(f"Збережено {path}")
    finally:
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
