"""Малювання рамок, підписів і HUD у єдиному стилі для обох програм."""
from __future__ import annotations

import cv2

# Кольори у форматі BGR
COLOR_OBJECT = (0, 200, 0)          # зелений — об'єкти
COLOR_FACE_KNOWN = (0, 220, 255)    # жовтий — впізнане обличчя
COLOR_FACE_UNKNOWN = (0, 0, 255)    # червоний — невідоме обличчя
COLOR_HUD_BG = (0, 0, 0)
COLOR_HUD_TEXT = (255, 255, 255)

FONT = cv2.FONT_HERSHEY_SIMPLEX


def draw_detection(frame, xyxy, label: str, color=COLOR_OBJECT, thickness: int = 2):
    """Намалювати рамку (x1,y1,x2,y2) з підписом над нею."""
    x1, y1, x2, y2 = (int(v) for v in xyxy)
    cv2.rectangle(frame, (x1, y1), (x2, y2), color, thickness)
    if label:
        (tw, th), bl = cv2.getTextSize(label, FONT, 0.5, 1)
        top = max(0, y1 - th - bl - 4)
        cv2.rectangle(frame, (x1, top), (x1 + tw + 4, top + th + bl + 4), color, -1)
        cv2.putText(frame, label, (x1 + 2, top + th + 2), FONT, 0.5, (0, 0, 0), 1, cv2.LINE_AA)
    return frame


def draw_hud(frame, lines: list[str]):
    """Напівпрозорий блок зверху-зліва з рядками статусу."""
    pad, line_h, width = 6, 20, 300
    height = pad * 2 + line_h * len(lines)
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (width, height), COLOR_HUD_BG, -1)
    cv2.addWeighted(overlay, 0.45, frame, 0.55, 0, frame)
    y = pad + 14
    for ln in lines:
        cv2.putText(frame, ln, (pad, y), FONT, 0.5, COLOR_HUD_TEXT, 1, cv2.LINE_AA)
        y += line_h
    return frame
