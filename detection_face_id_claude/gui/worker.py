"""VideoWorker — фоновий потік: захоплення кадрів + інференс, без блокування UI.

Продуктивність: у режимі облич важкі моделі (YOLO + InsightFace) працюють раз на N кадрів,
між ними перемальовуються кешовані рамки — кадри показуються щоразу, тож FPS лишається високим.

Контроль порушень: якщо в кадрі є незнайома особа довше за `INTRUSION_SECONDS`, робиться
скріншот, а подія додається до списку інцидентів (звіт формує UI наприкінці сесії).

Сигнали:
- frame_ready(np.ndarray) — анотований BGR-кадр;
- stats_ready(dict)       — метрики для карток/графіків;
- incident(dict)          — зафіксовано незнайому особу (live-сповіщення);
- status(str)             — повідомлення в статус-бар;
- failed(str)             — фатальна помилка.
"""
from __future__ import annotations

import time

import cv2
import numpy as np
from PySide6.QtCore import QMutex, QMutexLocker, QThread, Signal

import config
from common.camera import FPSMeter
from common.drawing import draw_detection, COLOR_OBJECT, COLOR_FACE_KNOWN, COLOR_FACE_UNKNOWN


class VideoWorker(QThread):
    frame_ready = Signal(np.ndarray)
    stats_ready = Signal(dict)
    incident = Signal(dict)
    status = Signal(str)
    failed = Signal(str)

    def __init__(self, camera_index: int = 0) -> None:
        super().__init__()
        self._mutex = QMutex()
        self._camera_index = camera_index
        self._reopen = False
        self._running = False
        self._mode = "detection"          # 'detection' | 'faceid'
        self._conf = config.CONF
        self._threshold = config.FACE_THRESHOLD
        self._every = config.FACE_EVERY
        self._classes = None              # None або список id класів COCO
        self._snapshot = False
        self.detector = None
        self.identifier = None

        # стан контролю порушень
        self.incidents: list[dict] = []
        self._unknown_since: float | None = None
        self._streak_captured = False
        self._current_incident: dict | None = None

    # ---- thread-safe сетери (з UI-потоку) ----
    def set_mode(self, mode: str) -> None:
        with QMutexLocker(self._mutex):
            self._mode = mode

    def set_conf(self, value: float) -> None:
        with QMutexLocker(self._mutex):
            self._conf = value
        if self.detector is not None:
            self.detector.conf = value

    def set_threshold(self, value: float) -> None:
        with QMutexLocker(self._mutex):
            self._threshold = value
        if self.identifier is not None:
            self.identifier.threshold = value

    def set_every(self, value: int) -> None:
        with QMutexLocker(self._mutex):
            self._every = max(1, int(value))

    def set_classes(self, classes) -> None:
        with QMutexLocker(self._mutex):
            self._classes = classes

    def set_camera(self, index: int) -> None:
        with QMutexLocker(self._mutex):
            self._camera_index = index
            self._reopen = True

    def request_snapshot(self) -> None:
        with QMutexLocker(self._mutex):
            self._snapshot = True

    def get_incidents(self) -> list[dict]:
        return self.incidents

    def stop(self) -> None:
        self._running = False
        self.wait(3000)

    # ---- основний цикл ----
    def _open(self, index: int):
        cap = cv2.VideoCapture(index)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.FRAME_WIDTH)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.FRAME_HEIGHT)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # менша затримка: тримати лише свіжий кадр
        return cap

    def run(self) -> None:
        self._running = True
        self.status.emit("Завантаження моделі детекції (YOLO)…")
        try:
            from engine.detector import ObjectDetector
            self.detector = ObjectDetector(config.YOLO_MODEL, conf=self._conf,
                                           imgsz=config.YOLO_IMGSZ)
        except Exception as exc:  # noqa: BLE001
            self.failed.emit(f"Не вдалося завантажити YOLO: {exc}")
            return

        cap = self._open(self._camera_index)
        if not cap.isOpened():
            self.failed.emit(f"Камера {self._camera_index} недоступна (перевірте дозвіл).")
            return

        fps = FPSMeter()
        frame_idx = 0
        last_mode = None
        cached_faces = []
        cached_objects = []
        self.status.emit("Працює")

        while self._running:
            with QMutexLocker(self._mutex):
                mode, every = self._mode, max(1, self._every)
                classes = self._classes
                reopen, cam = self._reopen, self._camera_index
                self._reopen = False
                take_snap = self._snapshot
                self._snapshot = False

            if mode != last_mode:  # зміна режиму — скидаємо кеш і стрік порушень
                cached_faces, cached_objects = [], []
                self._reset_streak()
                last_mode = mode

            if reopen:
                cap.release()
                cap = self._open(cam)
                if not cap.isOpened():
                    self.failed.emit(f"Камера {cam} недоступна.")
                    break
                cached_faces, cached_objects = [], []

            ok, frame = cap.read()
            if not ok:
                self.failed.emit("Порожній кадр — камера від'єдналася?")
                break

            now = time.time()
            class_counts: dict[str, int] = {}
            confs: list[float] = []
            faces_payload: list[dict] = []

            if mode == "detection":
                for d in self.detector.detect(frame, classes=classes):
                    draw_detection(frame, d.xyxy, f"{d.name} {d.conf:.2f}", COLOR_OBJECT)
                    class_counts[d.name] = class_counts.get(d.name, 0) + 1
                    confs.append(d.conf)
            else:  # faceid — важкий інференс лише раз на `every` кадрів
                run_heavy = (frame_idx % every == 0) or (self.identifier is None)
                if run_heavy:
                    cached_objects = [d for d in self.detector.detect(frame)
                                      if d.name != "person"]
                    if self.identifier is None and not self._load_identifier():
                        break
                    cached_faces = self.identifier.identify(frame)

                for d in cached_objects:
                    draw_detection(frame, d.xyxy, f"{d.name} {d.conf:.2f}", COLOR_OBJECT)
                    class_counts[d.name] = class_counts.get(d.name, 0) + 1
                    confs.append(d.conf)
                for f in cached_faces:
                    color = COLOR_FACE_KNOWN if f.name != "Unknown" else COLOR_FACE_UNKNOWN
                    draw_detection(frame, f.xyxy, f"{f.name} {f.score:.2f}", color)
                    faces_payload.append({"name": f.name, "score": f.score})

                unknown_count = sum(1 for f in faces_payload if f["name"] == "Unknown")
                self._check_intrusion(frame, unknown_count, now)

            fps.tick()
            if take_snap:
                config.DATA_DIR.mkdir(parents=True, exist_ok=True)
                path = config.DATA_DIR / f"shot_{int(now)}.jpg"
                cv2.imwrite(str(path), frame)
                self.status.emit(f"Збережено {path.name}")

            known = sum(1 for f in faces_payload if f["name"] != "Unknown")
            self.frame_ready.emit(frame.copy())
            self.stats_ready.emit({
                "fps": fps.fps,
                "mode": mode,
                "object_total": sum(class_counts.values()),
                "unique_classes": len(class_counts),
                "avg_conf": (sum(confs) / len(confs)) if confs else 0.0,
                "class_counts": class_counts,
                "faces": faces_payload,
                "known": known,
                "unknown": len(faces_payload) - known,
                "best_score": max((f["score"] for f in faces_payload), default=0.0),
                "db_size": self.identifier.size if self.identifier else 0,
                "incidents": len(self.incidents),
            })
            frame_idx += 1

        # фіналізуємо тривалість незавершеного стріку
        if self._unknown_since is not None and self._current_incident is not None:
            self._current_incident["duration"] = round(time.time() - self._unknown_since, 1)
        cap.release()
        self.status.emit("Зупинено")

    # ---- контроль порушень ----
    def _reset_streak(self) -> None:
        self._unknown_since = None
        self._streak_captured = False
        self._current_incident = None

    def _check_intrusion(self, frame, unknown_count: int, now: float) -> None:
        if unknown_count > 0:
            if self._unknown_since is None:
                self._unknown_since = now
                self._streak_captured = False
            elif not self._streak_captured and (now - self._unknown_since) >= config.INTRUSION_SECONDS:
                self._streak_captured = True
                self._save_incident(frame, now)
        else:
            if self._unknown_since is not None and self._current_incident is not None:
                self._current_incident["duration"] = round(now - self._unknown_since, 1)
            self._reset_streak()

    def _save_incident(self, frame, now: float) -> None:
        config.INCIDENTS_DIR.mkdir(parents=True, exist_ok=True)
        stamp = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime(now))
        path = config.INCIDENTS_DIR / f"intruder_{stamp}.jpg"
        cv2.imwrite(str(path), frame)
        incident = {
            "epoch": now,
            "time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(now)),
            "screenshot": str(path),
            "duration": None,
        }
        self.incidents.append(incident)
        self._current_incident = incident
        self.incident.emit(incident)
        self.status.emit(f"⚠ Невідома особа — знято скріншот {path.name}")

    def _load_identifier(self) -> bool:
        """Лениве завантаження InsightFace. False → фатально."""
        self.status.emit("Завантаження моделі облич (InsightFace)…")
        try:
            from engine.face_identifier import FaceIdentifier
            self.identifier = FaceIdentifier(
                config.DB_PATH, threshold=self._threshold, det_size=config.FACE_DET_SIZE)
        except FileNotFoundError:
            self.failed.emit("Немає бази облич. Спочатку побудуйте її через enroll.py.")
            return False
        except Exception as exc:  # noqa: BLE001
            self.failed.emit(f"InsightFace помилка: {exc}")
            return False
        self.status.emit("Працює")
        return True
