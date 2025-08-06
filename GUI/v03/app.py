import sys
import os
import threading
import configparser

from PySide6.QtWidgets import (
    QWidget, QLabel, QTextEdit, QVBoxLayout, QHBoxLayout, QApplication, QPushButton
)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, QUrl, QTimer
from PySide6.QtGui import QDesktopServices

# ==== BASE_DIR ====
if getattr(sys, 'frozen', False):
    base_dir = os.path.dirname(sys.executable)
else:
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# ==== Paths ====
assets_dir = os.path.join(base_dir, 'GUI', 'Assets')
pictures_dir = os.path.join(assets_dir, 'Pictures')
banners_dir = os.path.join(assets_dir, 'Banners')

image_path = os.path.join(pictures_dir, '1.png')
banner_singleplayer = os.path.join(banners_dir, 'SINGLEPLAYER.png')
banner_console = os.path.join(banners_dir, 'CONSOLE.png')
banner_prisoner = os.path.join(banners_dir, 'PRISONER.png')
banner_flagzones = os.path.join(banners_dir, 'FLAGZONES.png')
banner_supportmywork = os.path.join(banners_dir, 'SUPPORTMYWORK.png')
banner_buymeacoffee = os.path.join(banners_dir, 'BUYMEACOFFEE.png')

data_path = os.path.join(base_dir, 'data.ini')
data_config = configparser.ConfigParser()

MAX_LINES = 64

# ==== Statický import logiky ====
from Modules.Singleplayer.SaveItems.v32 import logic


class App(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SCUM Quality of Life v0.3.3.2 beta")
        self.setMinimumSize(520, 820)
        self.setMaximumSize(520, 820)
        self.setStyleSheet("background-color: #242424;")

        layout = QVBoxLayout()

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignLeft)
        pixmap = QPixmap(image_path)
        self.image_label.setPixmap(pixmap.scaledToWidth(500) if not pixmap.isNull() else None)
        self.image_label.setText("Obrázok sa nepodarilo načítať.") if pixmap.isNull() else None
        layout.addWidget(self.image_label)

        self.banner1_label = QLabel()
        self.banner1_label.setAlignment(Qt.AlignLeft)
        banner1_pixmap = QPixmap(banner_singleplayer)
        self.banner1_label.setPixmap(banner1_pixmap.scaledToWidth(520) if not banner1_pixmap.isNull() else None)
        self.banner1_label.setText("Banner SINGLEPLAYER sa nepodarilo načítať.") if banner1_pixmap.isNull() else None
        layout.addWidget(self.banner1_label)

        prisoner_layout = QHBoxLayout()
        self.prisoner_banner = QLabel()
        prisoner_pixmap = QPixmap(banner_prisoner)
        self.prisoner_banner.setPixmap(prisoner_pixmap.scaledToHeight(20, Qt.SmoothTransformation)) if not prisoner_pixmap.isNull() else None
        self.prisoner_value = QLabel("Loading...")
        self.prisoner_value.setStyleSheet("font-size:18px; color:#CCCCCC; margin-left:10px;")
        prisoner_layout.addWidget(self.prisoner_banner)
        prisoner_layout.addWidget(self.prisoner_value)
        prisoner_layout.addStretch()
        layout.addLayout(prisoner_layout)

        flagzones_layout = QHBoxLayout()
        self.flagzones_banner = QLabel()
        flagzones_pixmap = QPixmap(banner_flagzones)
        self.flagzones_banner.setPixmap(flagzones_pixmap.scaledToHeight(20, Qt.SmoothTransformation)) if not flagzones_pixmap.isNull() else None
        self.flagzones_value = QLabel("0")
        self.flagzones_value.setStyleSheet("font-size:18px; color:#FF9900; margin-left:10px;")
        flagzones_layout.addWidget(self.flagzones_banner)
        flagzones_layout.addWidget(self.flagzones_value)
        flagzones_layout.addStretch()
        layout.addLayout(flagzones_layout)

        self.banner2_label = QLabel()
        self.banner2_label.setAlignment(Qt.AlignLeft)
        banner2_pixmap = QPixmap(banner_console)
        self.banner2_label.setPixmap(banner2_pixmap.scaledToWidth(520) if not banner2_pixmap.isNull() else None)
        self.banner2_label.setText("Banner CONSOLE sa nepodarilo načítať.") if banner2_pixmap.isNull() else None
        layout.addWidget(self.banner2_label)

        self.console = QTextEdit()
        self.console.setReadOnly(True)
        layout.addWidget(self.console)

        self.banner3_label = QLabel()
        self.banner3_label.setAlignment(Qt.AlignLeft)
        banner3_pixmap = QPixmap(banner_supportmywork)
        self.banner3_label.setPixmap(banner3_pixmap.scaledToWidth(550) if not banner3_pixmap.isNull() else None)
        self.banner3_label.setText("Banner SUPPORTMYWORK sa nepodarilo načítať.") if banner3_pixmap.isNull() else None
        layout.addWidget(self.banner3_label)

        buyme_layout = QHBoxLayout()
        self.banner4_label = QLabel()
        self.banner4_label.setAlignment(Qt.AlignLeft)
        banner4_pixmap = QPixmap(banner_buymeacoffee)
        self.banner4_label.setPixmap(banner4_pixmap.scaledToHeight(28, Qt.SmoothTransformation)) if not banner4_pixmap.isNull() else None
        self.banner4_label.setText("Banner BUYMEACOFFEE sa nepodarilo načítať.") if banner4_pixmap.isNull() else None
        buyme_layout.addWidget(self.banner4_label)

        self.buy_coffee_btn = QPushButton("☕ Buy me a coffee")
        self.buy_coffee_btn.setStyleSheet("""
            background-color: #FFDD00;
            color: black;
            font-family: 'Cookie', cursive;
            font-size: 16px;
            font-weight: bold;
            border: 2px solid black;
            padding: 6px 16px;
            border-radius: 8px;
            margin-left: 15px;
        """)
        self.buy_coffee_btn.setFixedHeight(32)
        self.buy_coffee_btn.clicked.connect(self.open_coffee_link)
        buyme_layout.addWidget(self.buy_coffee_btn)
        buyme_layout.addStretch()
        layout.addLayout(buyme_layout)

        self.setLayout(layout)

        self.data_timer = QTimer(self)
        self.data_timer.timeout.connect(self.update_from_data_file)
        self.data_timer.start(1000)

        self.log("SCUM Quality of Life", color="orange")
        self.update_from_data_file()

        self.stop_event = threading.Event()
        self.logic_thread = threading.Thread(target=logic.logic_main_loop, args=(self, self.stop_event), daemon=True)
        self.logic_thread.start()

    def log(self, text, color="#20FF20"):
        current_text = self.console.toHtml()
        new_line = f'<span style="color:{color}">{text}</span><br>'
        self.console.setHtml(current_text + new_line)
        self.console.verticalScrollBar().setValue(self.console.verticalScrollBar().maximum())

    def thread_safe_log(self, text, color="#20FF20"):
        QTimer.singleShot(0, lambda: self.log(text, color))

    def update_prisoner_name(self, name: str):
        self.prisoner_value.setText(name)

    def update_flag_zones(self, count):
        self.flagzones_value.setText(str(count))
        self.thread_safe_log(f"[GUI] Zmenený počet základní: {count}", color="#FFFF00")

    def open_coffee_link(self):
        url = QUrl("https://www.buymeacoffee.com/jastronit")
        QDesktopServices.openUrl(url)

    def update_from_data_file(self):
        if not os.path.exists(data_path):
            return
        try:
            data_config.read(data_path)

            if 'prisoner' in data_config:
                name = data_config['prisoner'].get('name', 'Unknown')
                self.prisoner_value.setText(name)

            if 'flagzones' in data_config:
                count = data_config['flagzones'].getint('count', 0)
                self.flagzones_value.setText(str(count))

            log_path = os.path.join(base_dir, 'log.txt')
            if os.path.exists(log_path):
                with open(log_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()[-MAX_LINES:]
                    html = "".join(f"<span>{line.strip()}</span><br>" for line in lines)
                    self.console.setHtml(html)
                    self.console.verticalScrollBar().setValue(self.console.verticalScrollBar().maximum())
        except Exception as e:
            self.thread_safe_log(f"[GUI] Chyba pri čítaní data.ini: {e}", color="red")

    def closeEvent(self, event):
        self.stop_event.set()
        self.logic_thread.join()
        event.accept()


def run_gui(app: QApplication):
    window = App()
    window.show()
    exit_code = app.exec()
    sys.exit(exit_code)


if __name__ in ("__main__", "__nuitka__"):
    app = QApplication(sys.argv)
    run_gui(app)

