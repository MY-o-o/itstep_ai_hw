"""Програма 2 — розпізнавання об'єктів + ідентифікація облич на живому потоці.

Об'єкти: YOLO (COCO). Обличчя: InsightFace ArcFace проти бази data/db/face_db.npz.

Запуск (спочатку enroll.py для бази):
    python program2_face_id/identify_stream.py --camera 0
Клавіша 'q' — вихід.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import cv2

import config
from common.camera import open_camera, FPSMeter
from common.drawing import draw_detection, draw_hud, COLOR_OBJECT, COLOR_FACE_KNOWN, COLOR_FACE_UNKNOWN
from engine.detector import ObjectDetector
from engine.face_identifier import FaceIdentifier


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Ідентифікація облич + детекція об'єктів на потоці.")
    p.add_argument("--camera", type=int, default=config.CAMERA_INDEX)
    p.add_argument("--db", default=str(config.DB_PATH))
    p.add_argument("--threshold", type=float, default=config.FACE_THRESHOLD)
    p.add_argument("--yolo-model", default=config.YOLO_MODEL)
    p.add_argument("--conf", type=float, default=config.CONF)
    p.add_argument("--every", type=int, default=config.FACE_EVERY,
                   help="Розпізнавати обличчя кожні N кадрів")
    return p.parse_args()


def main() -> None:
    args = parse_args()

    if not Path(args.db).exists():
        print(f"Немає бази {args.db}. Спочатку запустіть enroll.py.")
        return

    print(f"Завантаження YOLO {args.yolo_model} ...")
    detector = ObjectDetector(args.yolo_model, conf=args.conf)
    print("Ініціалізація InsightFace ...")
    identifier = FaceIdentifier(args.db, threshold=args.threshold)
    print(f"База завантажена: {identifier.size} осіб.")

    cap = open_camera(args.camera, config.FRAME_WIDTH, config.FRAME_HEIGHT)
    fps = FPSMeter()
    frame_idx = 0
    cached_faces = []  # оновлюється кожні N кадрів
    print("Запущено. 'q' — вихід.")

    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                print("Порожній кадр — камера недоступна?")
                break

            # --- об'єкти (крім 'person' — обличчя позначимо окремо) ---
            obj_count = 0
            for d in detector.detect(frame):
                if d.name == "person":
                    continue
                obj_count += 1
                draw_detection(frame, d.xyxy, f"{d.name} {d.conf:.2f}", COLOR_OBJECT)

            # --- обличчя: розпізнаємо кожні N кадрів, між ними малюємо з кешу ---
            if frame_idx % max(1, args.every) == 0:
                cached_faces = identifier.identify(frame)
            for f in cached_faces:
                color = COLOR_FACE_KNOWN if f.name != "Unknown" else COLOR_FACE_UNKNOWN
                draw_detection(frame, f.xyxy, f"{f.name} {f.score:.2f}", color)

            fps.tick()
            draw_hud(frame, [
                f"FPS: {fps.fps:4.1f}",
                f"Об'єктів: {obj_count}  Облич: {len(cached_faces)}",
                f"База: {identifier.size} осіб  поріг {args.threshold:.2f}",
            ])
            cv2.imshow("Програма 2 — ідентифікація облич + об'єкти", frame)

            if (cv2.waitKey(1) & 0xFF) == ord("q"):
                break
            frame_idx += 1
    finally:
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
