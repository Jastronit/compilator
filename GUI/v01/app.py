import sys
import os
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout
from CustomTools.CPrint import cprint

# ---- BASE_DIR Setup ----
if getattr(sys, 'frozen', False):
    base_dir = os.path.dirname(sys.executable)
else:
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# ---- GUI Logic ----
def run_gui(app):
    cprint.console("info", "[app v0.1] Spúšťam GUI...")

    window = QWidget()
    window.setWindowTitle("SCUM GUI v0.1")

    layout = QVBoxLayout()
    layout.addWidget(QLabel("Vitaj v SCUM GUI verzii 0.1"))
    layout.addWidget(QLabel("Toto je testovacie GUI"))

    window.setLayout(layout)
    window.resize(400, 150)
    window.show()

    # ✅ Kriticky dôležité: uchovať referenciu na okno,
    # inak sa zničí po skončení tejto funkcie
    app._main_window = window

