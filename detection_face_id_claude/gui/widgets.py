"""Перевикористовувані віджети дашборду у стилі HIG."""
from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QButtonGroup, QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget,
)


class Card(QFrame):
    """Контейнер-картка зі скругленням (стиль задає QSS #Card)."""

    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("Card")


class StatCard(QFrame):
    """KPI-плитка: велике значення + підпис."""

    def __init__(self, title: str, value: str = "—") -> None:
        super().__init__()
        self.setObjectName("Card")
        self.setMinimumHeight(78)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(14, 10, 14, 10)
        lay.setSpacing(2)
        self._value = QLabel(value)
        self._value.setObjectName("Metric")
        caption = QLabel(title)
        caption.setObjectName("Caption")
        caption.setWordWrap(True)            # довгі підписи переносяться, а не обрізаються
        lay.addWidget(self._value)
        lay.addWidget(caption)
        lay.addStretch(1)

    def set_value(self, text: str) -> None:
        self._value.setText(text)


class SegmentedControl(QWidget):
    """Сегментований перемикач у стилі NSSegmentedControl."""

    changed = Signal(str)

    def __init__(self, options: list[tuple[str, str]]) -> None:
        super().__init__()
        self.setObjectName("SegmentBar")
        lay = QHBoxLayout(self)
        lay.setContentsMargins(2, 2, 2, 2)
        lay.setSpacing(2)

        self._buttons: dict[str, QPushButton] = {}
        group = QButtonGroup(self)
        group.setExclusive(True)
        for key, label in options:
            btn = QPushButton(label)
            btn.setObjectName("Segment")
            btn.setCheckable(True)
            btn.setCursor(Qt.PointingHandCursor)
            group.addButton(btn)
            lay.addWidget(btn)
            btn.clicked.connect(lambda _=False, k=key: self._select(k))
            self._buttons[key] = btn

        self._current = options[0][0]
        self._buttons[self._current].setChecked(True)

    def _select(self, key: str) -> None:
        self._current = key
        self._buttons[key].setChecked(True)
        self.changed.emit(key)

    def current(self) -> str:
        return self._current

    def set_current(self, key: str) -> None:
        self._current = key
        self._buttons[key].setChecked(True)
