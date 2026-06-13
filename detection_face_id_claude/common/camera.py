"""Робота з камерою: відкриття, перебір пристроїв, лічильник FPS."""
from __future__ import annotations

import time
from collections import deque

import cv2


def open_camera(index: int = 0, width: int = 1280, height: int = 720) -> "cv2.VideoCapture":
    """Відкрити камеру за індексом. Кидає RuntimeError, якщо не вдалося."""
    cap = cv2.VideoCapture(index)
    if not cap.isOpened():
        raise RuntimeError(
            f"Не вдалося відкрити камеру з індексом {index}. "
            f"Перевірте дозвіл (macOS: System Settings → Privacy & Security → Camera) "
            f"або спробуйте інший --camera (див. list_cameras)."
        )
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    return cap


def list_cameras(max_index: int = 5) -> list[int]:
    """Повернути індекси камер, з яких реально читається кадр (0..max_index)."""
    available: list[int] = []
    for i in range(max_index + 1):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            ok, _ = cap.read()
            if ok:
                available.append(i)
        cap.release()
    return available


class FPSMeter:
    """Ковзний FPS за останніми `window` кадрами."""

    def __init__(self, window: int = 30) -> None:
        self._ts: deque[float] = deque(maxlen=window)

    def tick(self) -> None:
        self._ts.append(time.time())

    @property
    def fps(self) -> float:
        if len(self._ts) < 2:
            return 0.0
        span = self._ts[-1] - self._ts[0]
        return (len(self._ts) - 1) / span if span > 0 else 0.0


if __name__ == "__main__":
    # Швидка діагностика: які камери доступні
    print("Доступні камери:", list_cameras())
