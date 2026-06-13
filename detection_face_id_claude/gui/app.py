"""Точка входу GUI: QApplication + Apple-HIG-тема + головне вікно.

Запуск:
    python gui/app.py
"""
from __future__ import annotations

import sys
from pathlib import Path

# Корінь пакета у sys.path → працюють `import config` / `from gui...` / `from engine...`
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PySide6.QtWidgets import QApplication

from gui import theme
from gui.main_window import MainWindow


def main() -> None:
    app = QApplication(sys.argv)
    theme.apply_appearance(app, dark=True)
    window = MainWindow(app)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
