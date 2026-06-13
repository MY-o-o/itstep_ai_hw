"""Тема в стилі Apple Human Interface Guidelines для PySide6 (світла/темна).

Замість Material — системні кольори macOS, шрифт San Francisco, м'які картки зі
скругленнями, accent-кнопки, сегментовані контролі та повзунки macOS-вигляду.
Графіки навмисно фарбуються системно-сірим (`AXIS_GRAY`), що читається на обох темах.
"""
from __future__ import annotations

from PySide6.QtGui import QFont

# Системні палітри (наближення до HIG)
DARK = {
    "bg": "#1e1e1e",
    "card": "#2c2c2e",
    "control": "#3a3a3c",
    "control_hover": "#48484a",
    "border": "rgba(255,255,255,0.10)",
    "text": "#ffffff",
    "secondary": "rgba(235,235,245,0.60)",
    "accent": "#0A84FF",
    "accent_hover": "#3a9bff",
    "muted": "#48484a",
    "segment_track": "#3a3a3c",
    "segment_sel": "rgba(255,255,255,0.22)",
}
LIGHT = {
    "bg": "#ECECEC",
    "card": "#ffffff",
    "control": "#ffffff",
    "control_hover": "#f0f0f2",
    "border": "rgba(0,0,0,0.10)",
    "text": "#000000",
    "secondary": "rgba(60,60,67,0.60)",
    "accent": "#007AFF",
    "accent_hover": "#1f86ff",
    "muted": "#c7c7cc",
    "segment_track": "#e3e3e6",
    "segment_sel": "#ffffff",
}

# Системні кольори акцентів для графіків (HIG system colors)
AXIS_GRAY = "#8E8E93"
C_BLUE = (10, 132, 255)
C_GREEN = (48, 209, 88)
C_RED = (255, 69, 58)
C_ORANGE = (255, 159, 10)
C_TEAL = (64, 200, 224)


def colors(dark: bool) -> dict:
    return DARK if dark else LIGHT


def stylesheet(dark: bool) -> str:
    c = colors(dark)
    return f"""
    QWidget {{ color: {c['text']}; font-size: 13px; }}
    QMainWindow, QWidget#Root {{ background: {c['bg']}; }}
    QFrame#Card {{ background: {c['card']}; border: 1px solid {c['border']}; border-radius: 12px; }}

    QLabel#Title {{ font-size: 22px; font-weight: 700; }}
    QLabel#Header {{ font-size: 15px; font-weight: 600; }}
    QLabel#Caption {{ color: {c['secondary']}; font-size: 12px; }}
    QLabel#Metric {{ font-size: 24px; font-weight: 600; }}

    QPushButton {{
        background: {c['control']}; border: 1px solid {c['border']};
        border-radius: 8px; padding: 6px 14px;
    }}
    QPushButton:hover {{ background: {c['control_hover']}; }}
    QPushButton#Primary {{ background: {c['accent']}; color: white; border: none; font-weight: 600; }}
    QPushButton#Primary:hover {{ background: {c['accent_hover']}; }}
    QPushButton#Primary:disabled {{ background: {c['muted']}; color: rgba(255,255,255,0.6); }}

    QWidget#SegmentBar {{ background: {c['segment_track']}; border-radius: 9px; }}
    QPushButton#Segment {{ background: transparent; border: none; border-radius: 7px;
        padding: 5px 16px; color: {c['secondary']}; }}
    QPushButton#Segment:checked {{ background: {c['segment_sel']}; color: {c['text']}; font-weight: 600; }}

    QSlider::groove:horizontal {{ height: 4px; background: {c['border']}; border-radius: 2px; }}
    QSlider::sub-page:horizontal {{ background: {c['accent']}; border-radius: 2px; }}
    QSlider::handle:horizontal {{ width: 18px; height: 18px; margin: -7px 0; border-radius: 9px;
        background: white; border: 1px solid rgba(0,0,0,0.18); }}

    QCheckBox {{ spacing: 8px; }}
    QCheckBox::indicator {{ width: 18px; height: 18px; border-radius: 5px;
        border: 1px solid {c['border']}; background: {c['control']}; }}
    QCheckBox::indicator:checked {{ background: {c['accent']}; border: none; }}

    QComboBox {{ background: {c['control']}; border: 1px solid {c['border']};
        border-radius: 7px; padding: 4px 10px; }}
    QComboBox QAbstractItemView {{ background: {c['card']}; selection-background-color: {c['accent']}; }}

    QProgressBar {{ background: {c['border']}; border: none; border-radius: 4px;
        height: 8px; text-align: center; color: transparent; }}
    QProgressBar::chunk {{ background: {c['accent']}; border-radius: 4px; }}

    QListWidget {{ background: transparent; border: none; }}
    QScrollArea {{ background: transparent; border: none; }}
    QScrollBar:vertical {{ background: transparent; width: 8px; margin: 2px; }}
    QScrollBar::handle:vertical {{ background: {c['muted']}; border-radius: 4px; min-height: 24px; }}
    QScrollBar::add-line, QScrollBar::sub-line {{ height: 0; }}
    QStatusBar {{ color: {c['secondary']}; }}
    """


def apply_appearance(app, dark: bool) -> None:
    """Застосувати шрифт SF + таблицю стилів обраної теми до всього застосунку."""
    app.setFont(QFont(".AppleSystemUIFont", 13))
    app.setStyleSheet(stylesheet(dark))
