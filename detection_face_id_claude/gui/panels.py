"""Панелі-інспектори для кожного режиму роботи.

- `DetectionPanel` — інструменти, графіки й метрики ЛИШЕ для детекції об'єктів.
- `FacePanel` — інструменти, графіки й метрики ЛИШЕ для ідентифікації облич.

Обидві — QScrollArea з колонкою карток; оновлюються через `update_stats(dict)`.
"""
from __future__ import annotations

from collections import deque

import pyqtgraph as pg
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QCheckBox, QGridLayout, QHBoxLayout, QLabel, QListWidget, QProgressBar,
    QScrollArea, QSlider, QVBoxLayout, QWidget,
)

import config
from gui.theme import AXIS_GRAY, C_BLUE, C_GREEN, C_RED, C_ORANGE, C_TEAL
from gui.widgets import Card, StatCard

pg.setConfigOption("background", None)
pg.setConfigOption("foreground", AXIS_GRAY)
pg.setConfigOptions(antialias=True)


# ---------- спільні будівельні блоки ----------
def _caption(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setObjectName("Caption")
    return lbl


def _header(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setObjectName("Header")
    return lbl


def _line_plot(color, height: int = 130, fill: bool = True):
    plot = pg.PlotWidget()
    plot.setMaximumHeight(height)
    plot.setMenuEnabled(False)
    plot.showGrid(x=False, y=True, alpha=0.15)
    plot.getPlotItem().hideButtons()
    brush = pg.mkBrush((*color, 45)) if fill else None
    curve = plot.plot(pen=pg.mkPen(color, width=2),
                      fillLevel=0 if fill else None, brush=brush)
    return plot, curve


def _bar_plot(color, height: int = 150):
    plot = pg.PlotWidget()
    plot.setMaximumHeight(height)
    plot.setMenuEnabled(False)
    plot.showGrid(x=False, y=True, alpha=0.15)
    plot.getPlotItem().hideButtons()
    item = pg.BarGraphItem(x=[0], height=[0], width=0.6, brush=pg.mkBrush(color))
    plot.addItem(item)
    axis = plot.getAxis("bottom")
    axis.setStyle(tickFont=QFont(".AppleSystemUIFont", 8), tickTextOffset=4)
    axis.setHeight(26)
    return plot, item


def _set_bar(item, plot, pairs):
    """Оновити барчарт парами (label, value); довгі підписи обрізаються."""
    pairs = pairs[:6]
    xs = list(range(len(pairs)))
    item.setOpts(x=xs or [0], height=[v for _, v in pairs] or [0], width=0.6)
    labels = [(name[:9] + "…") if len(name) > 10 else name for name, _ in pairs]
    plot.getAxis("bottom").setTicks([list(zip(xs, labels))])


def _slider(value: int, lo: int = 0, hi: int = 100):
    s = QSlider(Qt.Horizontal)
    s.setRange(lo, hi)
    s.setValue(value)
    return s


def _card_with(*widgets) -> Card:
    card = Card()
    lay = QVBoxLayout(card)
    lay.setContentsMargins(14, 12, 14, 14)
    lay.setSpacing(8)
    for w in widgets:
        if isinstance(w, QWidget):
            lay.addWidget(w)
        else:
            lay.addLayout(w)
    return card


def _scroll_body():
    """Повертає (scrollArea, vbox) — колонку всередині прокручуваної області."""
    area = QScrollArea()
    area.setWidgetResizable(True)
    area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    body = QWidget()
    area.setWidget(body)
    col = QVBoxLayout(body)
    col.setContentsMargins(0, 0, 0, 0)
    col.setSpacing(12)
    return area, col


# ====================================================================
class DetectionPanel(QScrollArea):
    """Інспектор режиму ДЕТЕКЦІЇ."""

    conf_changed = Signal(float)
    classes_changed = Signal(object)  # None або [0]

    def __init__(self) -> None:
        super().__init__()
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        body = QWidget()
        self.setWidget(body)
        col = QVBoxLayout(body)
        col.setContentsMargins(0, 0, 0, 0)
        col.setSpacing(12)

        self._fps_hist: deque[float] = deque(maxlen=120)
        self._obj_hist: deque[int] = deque(maxlen=120)
        self._seen: set[str] = set()
        self._total = 0

        # --- KPI (6 карток) ---
        grid_card = Card()
        grid = QGridLayout(grid_card)
        grid.setContentsMargins(12, 12, 12, 12)
        grid.setSpacing(10)
        self.kpi_fps = StatCard("FPS")
        self.kpi_obj = StatCard("Об'єктів у кадрі")
        self.kpi_cls = StatCard("Класів у кадрі")
        self.kpi_conf = StatCard("Сер. впевненість")
        self.kpi_total = StatCard("Усього детекцій")
        self.kpi_seen = StatCard("Класів за сесію")
        for i, c in enumerate((self.kpi_fps, self.kpi_obj, self.kpi_cls,
                               self.kpi_conf, self.kpi_total, self.kpi_seen)):
            grid.addWidget(c, i // 2, i % 2)
        col.addWidget(grid_card)

        # --- контроли (ЛИШЕ для детекції) ---
        self.conf_lbl = _caption(f"Впевненість детекції: {config.CONF:.2f}")
        self.conf_slider = _slider(int(config.CONF * 100))
        self.conf_slider.valueChanged.connect(
            lambda v: self.conf_lbl.setText(f"Впевненість детекції: {v / 100:.2f}"))
        self.conf_slider.valueChanged.connect(lambda v: self.conf_changed.emit(v / 100.0))

        self.only_people = QCheckBox("Лише люди (клас person)")
        self.only_people.toggled.connect(
            lambda on: self.classes_changed.emit([0] if on else None))

        self.conf_bar = QProgressBar()
        self.conf_bar.setRange(0, 100)
        self.conf_bar.setTextVisible(False)
        col.addWidget(_card_with(_header("Інструменти детекції"),
                                 self.conf_lbl, self.conf_slider, self.only_people,
                                 _caption("Середня впевненість кадру"), self.conf_bar))

        # --- графіки ---
        self.fps_plot, self.fps_curve = _line_plot(C_BLUE)
        col.addWidget(_card_with(_header("FPS у часі"), self.fps_plot))

        self.obj_plot, self.obj_curve = _line_plot(C_TEAL)
        col.addWidget(_card_with(_header("Об'єктів у кадрі (у часі)"), self.obj_plot))

        self.bar_plot, self.bar_item = _bar_plot(C_BLUE, height=160)
        col.addWidget(_card_with(_header("Об'єкти за класами (зараз)"), self.bar_plot))

        # --- детальний список ---
        self.class_list = QListWidget()
        self.class_list.setMaximumHeight(120)
        col.addWidget(_card_with(_header("Класи в кадрі"), self.class_list))

        col.addStretch(1)

    # значення контролів для ініціалізації worker
    def conf_value(self) -> float:
        return self.conf_slider.value() / 100.0

    def classes_value(self):
        return [0] if self.only_people.isChecked() else None

    def update_stats(self, s: dict) -> None:
        self.kpi_fps.set_value(f"{s['fps']:.1f}")
        self.kpi_obj.set_value(str(s["object_total"]))
        self.kpi_cls.set_value(str(s["unique_classes"]))
        self.kpi_conf.set_value(f"{s['avg_conf'] * 100:.0f}%")

        self._total += s["object_total"]
        self._seen |= set(s["class_counts"])
        self.kpi_total.set_value(str(self._total))
        self.kpi_seen.set_value(str(len(self._seen)))
        self.conf_bar.setValue(int(s["avg_conf"] * 100))

        self._fps_hist.append(s["fps"])
        self._obj_hist.append(s["object_total"])
        self.fps_curve.setData(list(self._fps_hist))
        self.obj_curve.setData(list(self._obj_hist))

        items = sorted(s["class_counts"].items(), key=lambda kv: kv[1], reverse=True)[:6]
        _set_bar(self.bar_item, self.bar_plot, items)

        self.class_list.clear()
        for name, count in items:
            self.class_list.addItem(f"{name} — {count}")


# ====================================================================
class FacePanel(QScrollArea):
    """Інспектор режиму ІДЕНТИФІКАЦІЇ ОБЛИЧ."""

    threshold_changed = Signal(float)
    every_changed = Signal(int)

    def __init__(self) -> None:
        super().__init__()
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        body = QWidget()
        self.setWidget(body)
        col = QVBoxLayout(body)
        col.setContentsMargins(0, 0, 0, 0)
        col.setSpacing(12)

        self._fps_hist: deque[float] = deque(maxlen=120)
        self._known_hist: deque[int] = deque(maxlen=120)
        self._unknown_hist: deque[int] = deque(maxlen=120)
        self._people: set[str] = set()

        # --- KPI (6 карток) ---
        grid_card = Card()
        grid = QGridLayout(grid_card)
        grid.setContentsMargins(12, 12, 12, 12)
        grid.setSpacing(10)
        self.kpi_fps = StatCard("FPS")
        self.kpi_faces = StatCard("Облич у кадрі")
        self.kpi_known = StatCard("Впізнано")
        self.kpi_unknown = StatCard("Невідомих")
        self.kpi_db = StatCard("Осіб у базі")
        self.kpi_uniq = StatCard("Унікальних за сесію")
        for i, c in enumerate((self.kpi_fps, self.kpi_faces, self.kpi_known,
                               self.kpi_unknown, self.kpi_db, self.kpi_uniq)):
            grid.addWidget(c, i // 2, i % 2)
        col.addWidget(grid_card)

        # --- контроли (ЛИШЕ для облич) ---
        self.thr_lbl = _caption(f"Поріг впізнавання: {config.FACE_THRESHOLD:.2f}")
        self.thr_slider = _slider(int(config.FACE_THRESHOLD * 100))
        self.thr_slider.valueChanged.connect(
            lambda v: self.thr_lbl.setText(f"Поріг впізнавання: {v / 100:.2f}"))
        self.thr_slider.valueChanged.connect(lambda v: self.threshold_changed.emit(v / 100.0))

        self.every_lbl = _caption(f"Розпізнавати кожні {config.FACE_EVERY} кадр(и)")
        self.every_slider = _slider(config.FACE_EVERY, lo=1, hi=10)
        self.every_slider.valueChanged.connect(
            lambda v: self.every_lbl.setText(f"Розпізнавати кожні {v} кадр(и)"))
        self.every_slider.valueChanged.connect(lambda v: self.every_changed.emit(v))

        self.best_bar = QProgressBar()
        self.best_bar.setRange(0, 100)
        self.best_bar.setTextVisible(False)
        col.addWidget(_card_with(_header("Інструменти ідентифікації"),
                                 self.thr_lbl, self.thr_slider,
                                 self.every_lbl, self.every_slider,
                                 _caption("Найкращий збіг у кадрі"), self.best_bar))

        # --- графіки ---
        self.fps_plot, self.fps_curve = _line_plot(C_BLUE)
        col.addWidget(_card_with(_header("FPS у часі"), self.fps_plot))

        ku_card = Card()
        ku_lay = QVBoxLayout(ku_card)
        ku_lay.setContentsMargins(14, 12, 14, 14)
        ku_lay.setSpacing(8)
        ku_lay.addWidget(_header("Впізнано / Невідомо (у часі)"))
        self.ku_plot = pg.PlotWidget()
        self.ku_plot.setMaximumHeight(130)
        self.ku_plot.setMenuEnabled(False)
        self.ku_plot.showGrid(x=False, y=True, alpha=0.15)
        self.ku_plot.getPlotItem().hideButtons()
        self.known_curve = self.ku_plot.plot(
            pen=pg.mkPen(C_GREEN, width=2), fillLevel=0, brush=pg.mkBrush((*C_GREEN, 45)))
        self.unknown_curve = self.ku_plot.plot(pen=pg.mkPen(C_RED, width=2))
        legend = QLabel(
            '<span style="color:#30D158">●</span> впізнано&nbsp;&nbsp;&nbsp;'
            '<span style="color:#FF453A">●</span> невідомо')
        legend.setObjectName("Caption")
        legend.setTextFormat(Qt.RichText)
        ku_lay.addWidget(self.ku_plot)
        ku_lay.addWidget(legend)
        col.addWidget(ku_card)

        self.score_plot, self.score_item = _bar_plot(C_ORANGE, height=160)
        self.score_plot.setYRange(0, 1)
        col.addWidget(_card_with(_header("Схожість за обличчями (зараз)"), self.score_plot))

        # --- хто в кадрі ---
        self.people_list = QListWidget()
        self.people_list.setMaximumHeight(120)
        col.addWidget(_card_with(_header("Зараз у кадрі"), self.people_list))

        col.addStretch(1)

    def threshold_value(self) -> float:
        return self.thr_slider.value() / 100.0

    def every_value(self) -> int:
        return self.every_slider.value()

    def update_stats(self, s: dict) -> None:
        faces = s["faces"]
        self.kpi_fps.set_value(f"{s['fps']:.1f}")
        self.kpi_faces.set_value(str(len(faces)))
        self.kpi_known.set_value(str(s["known"]))
        self.kpi_unknown.set_value(str(s["unknown"]))
        self.kpi_db.set_value(str(s["db_size"]))

        self._people |= {f["name"] for f in faces if f["name"] != "Unknown"}
        self.kpi_uniq.set_value(str(len(self._people)))
        self.best_bar.setValue(int(s["best_score"] * 100))

        self._fps_hist.append(s["fps"])
        self._known_hist.append(s["known"])
        self._unknown_hist.append(s["unknown"])
        self.fps_curve.setData(list(self._fps_hist))
        self.known_curve.setData(list(self._known_hist))
        self.unknown_curve.setData(list(self._unknown_hist))

        items = [(f["name"], f["score"]) for f in faces][:6]
        _set_bar(self.score_item, self.score_plot, items)

        self.people_list.clear()
        for f in faces:
            self.people_list.addItem(f"{f['name']}  ({f['score']:.2f})")
