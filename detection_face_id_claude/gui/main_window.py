"""Головне вікно у стилі Apple HIG: тулбар, відео та інспектор, що залежить від режиму."""
from __future__ import annotations

import time
from pathlib import Path

import cv2
from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import (
    QApplication, QComboBox, QHBoxLayout, QLabel, QMainWindow, QMessageBox,
    QPushButton, QStackedWidget, QVBoxLayout, QWidget,
)

import config
from gui import theme
from gui.panels import DetectionPanel, FacePanel
from gui.widgets import Card, SegmentedControl
from gui.worker import VideoWorker


class MainWindow(QMainWindow):
    def __init__(self, app: QApplication) -> None:
        super().__init__()
        self._app = app
        self._dark = True
        self._incident_count = 0
        self.worker: VideoWorker | None = None

        self.setWindowTitle("Vision Studio")
        self.resize(1360, 860)
        self.setMinimumSize(1140, 720)  # не даємо стиснути вікно до накладання елементів

        root = QWidget()
        root.setObjectName("Root")
        self.setCentralWidget(root)
        outer = QVBoxLayout(root)
        outer.setContentsMargins(14, 14, 14, 14)
        outer.setSpacing(12)

        outer.addWidget(self._build_toolbar())

        content = QHBoxLayout()
        content.setSpacing(12)
        content.addWidget(self._build_video(), stretch=3)
        content.addWidget(self._build_inspector(), stretch=2)
        outer.addLayout(content)

        self.statusBar().showMessage("Готово. Натисніть «Старт».")

    # ---------------- тулбар ----------------
    def _build_toolbar(self) -> Card:
        bar = Card()
        lay = QHBoxLayout(bar)
        lay.setContentsMargins(14, 10, 14, 10)
        lay.setSpacing(12)

        title = QLabel("Vision Studio")
        title.setObjectName("Title")
        lay.addWidget(title)
        lay.addSpacing(8)

        self.mode_seg = SegmentedControl([
            ("detection", "Детекція"),
            ("faceid", "Обличчя"),
        ])
        self.mode_seg.changed.connect(self._on_mode)
        lay.addWidget(self.mode_seg)

        lay.addStretch(1)

        self.alert_lbl = QLabel()
        self.alert_lbl.setStyleSheet("color: #FF453A; font-weight: 600;")
        self.alert_lbl.setVisible(False)
        lay.addWidget(self.alert_lbl)

        lay.addWidget(QLabel("Камера"))
        self.camera_combo = QComboBox()
        self.camera_combo.addItems([str(i) for i in range(5)])
        self.camera_combo.setCurrentText(str(config.CAMERA_INDEX))
        self.camera_combo.currentTextChanged.connect(self._on_camera)
        lay.addWidget(self.camera_combo)

        self.appearance_seg = SegmentedControl([("dark", "Темна"), ("light", "Світла")])
        self.appearance_seg.changed.connect(lambda k: self._apply_theme(k == "dark"))
        lay.addWidget(self.appearance_seg)

        self.snap_btn = QPushButton("Знімок")
        self.snap_btn.setEnabled(False)
        self.snap_btn.clicked.connect(self._snapshot)
        lay.addWidget(self.snap_btn)

        self.run_btn = QPushButton("Старт")
        self.run_btn.setObjectName("Primary")
        self.run_btn.clicked.connect(self._toggle_run)
        lay.addWidget(self.run_btn)
        return bar

    # ---------------- відео ----------------
    def _build_video(self) -> Card:
        card = Card()
        lay = QVBoxLayout(card)
        lay.setContentsMargins(14, 14, 14, 14)
        lay.setSpacing(10)

        header = QLabel("Прямий потік")
        header.setObjectName("Header")
        lay.addWidget(header)

        self.video_label = QLabel("Натисніть «Старт», щоб увімкнути камеру")
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setMinimumSize(520, 360)
        self.video_label.setStyleSheet(
            "background: #0c0c0c; border-radius: 10px; color: #8E8E93;")
        lay.addWidget(self.video_label, stretch=1)
        return card

    # ---------------- інспектор (залежить від режиму) ----------------
    def _build_inspector(self) -> QStackedWidget:
        self.detection_panel = DetectionPanel()
        self.face_panel = FacePanel()
        self.detection_panel.conf_changed.connect(self._set_conf)
        self.detection_panel.classes_changed.connect(self._set_classes)
        self.face_panel.threshold_changed.connect(self._set_threshold)
        self.face_panel.every_changed.connect(self._set_every)

        self.inspector = QStackedWidget()
        self.inspector.setMinimumWidth(380)
        self.inspector.addWidget(self.detection_panel)  # index 0
        self.inspector.addWidget(self.face_panel)       # index 1
        self._panels = {"detection": self.detection_panel, "faceid": self.face_panel}
        self._panel_index = {"detection": 0, "faceid": 1}
        return self.inspector

    # ---------------- режим / тема ----------------
    def _on_mode(self, key: str) -> None:
        self.inspector.setCurrentIndex(self._panel_index[key])
        if self.worker:
            self.worker.set_mode(key)

    def _apply_theme(self, dark: bool) -> None:
        self._dark = dark
        theme.apply_appearance(self._app, dark)

    # ---------------- проксі контролів → worker ----------------
    def _set_conf(self, v: float) -> None:
        if self.worker:
            self.worker.set_conf(v)

    def _set_classes(self, classes) -> None:
        if self.worker:
            self.worker.set_classes(classes)

    def _set_threshold(self, v: float) -> None:
        if self.worker:
            self.worker.set_threshold(v)

    def _set_every(self, v: int) -> None:
        if self.worker:
            self.worker.set_every(v)

    def _on_camera(self, text: str) -> None:
        if self.worker:
            self.worker.set_camera(int(text))

    def _snapshot(self) -> None:
        if self.worker:
            self.worker.request_snapshot()

    # ---------------- життєвий цикл потоку ----------------
    def _toggle_run(self) -> None:
        if self.worker and self.worker.isRunning():
            self._stop_worker()
            self.statusBar().showMessage("Зупинено")
            return

        self._incident_count = 0
        self.alert_lbl.setVisible(False)
        self.worker = VideoWorker(int(self.camera_combo.currentText()))
        self.worker.set_mode(self.mode_seg.current())
        self.worker.set_conf(self.detection_panel.conf_value())
        self.worker.set_classes(self.detection_panel.classes_value())
        self.worker.set_threshold(self.face_panel.threshold_value())
        self.worker.set_every(self.face_panel.every_value())
        self.worker.frame_ready.connect(self._on_frame)
        self.worker.stats_ready.connect(self._on_stats)
        self.worker.incident.connect(self._on_incident)
        self.worker.status.connect(self.statusBar().showMessage)
        self.worker.failed.connect(self._on_failed)
        self.worker.start()
        self.run_btn.setText("Стоп")
        self.snap_btn.setEnabled(True)

    def _stop_worker(self) -> None:
        """Зупинити потік і сформувати звіт про порушення, якщо вони були."""
        if not self.worker:
            return
        worker = self.worker
        worker.stop()
        self.worker = None
        self.run_btn.setText("Старт")
        self.snap_btn.setEnabled(False)
        self._finish_session(worker)

    def _finish_session(self, worker: VideoWorker) -> None:
        incidents = worker.get_incidents()
        if not incidents:
            return
        path = self._write_report(incidents)
        self.statusBar().showMessage(f"Звіт про порушення збережено: {path}")
        QMessageBox.warning(
            self, "Звіт про порушення",
            f"Зафіксовано подій із незнайомими особами: {len(incidents)}\n\n"
            f"Скріншоти: {config.INCIDENTS_DIR}\nЗвіт: {path}")

    def _write_report(self, incidents: list[dict]) -> Path:
        config.REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        stamp = time.strftime("%Y-%m-%d_%H-%M-%S")
        path = config.REPORTS_DIR / f"incident_report_{stamp}.md"
        lines = [
            "# Звіт про порушення (незнайомі особи)",
            "",
            f"Згенеровано: {time.strftime('%Y-%m-%d %H:%M:%S')}",
            f"Усього подій: {len(incidents)}",
            "",
            "| № | Час виявлення | Тривалість, с | Скріншот |",
            "| - | ------------- | ------------- | -------- |",
        ]
        for i, inc in enumerate(incidents, 1):
            dur = inc.get("duration")
            dur_s = f"{dur:.1f}" if dur is not None else "—"
            lines.append(f"| {i} | {inc['time']} | {dur_s} | {Path(inc['screenshot']).name} |")
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return path

    def _on_incident(self, inc: dict) -> None:
        self._incident_count += 1
        self.alert_lbl.setText(f"⚠ Порушень: {self._incident_count}")
        self.alert_lbl.setVisible(True)
        self.statusBar().showMessage(f"⚠ Невідома особа зафіксована о {inc['time']}")

    def _on_failed(self, msg: str) -> None:
        self.statusBar().showMessage("Помилка: " + msg)
        self._stop_worker()

    # ---------------- слоти даних ----------------
    def _on_frame(self, frame) -> None:
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w = rgb.shape[:2]
        img = QImage(rgb.data, w, h, 3 * w, QImage.Format_RGB888)
        pix = QPixmap.fromImage(img).scaled(
            self.video_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.video_label.setPixmap(pix)

    def _on_stats(self, s: dict) -> None:
        self._panels[s["mode"]].update_stats(s)

    def closeEvent(self, event) -> None:  # noqa: N802 (Qt API)
        self._stop_worker()  # зупиняє потік і друкує звіт про порушення, якщо були
        event.accept()
