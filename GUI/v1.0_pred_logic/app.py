from PySide6.QtWidgets import (
    QWidget, QLabel, QTextEdit, QVBoxLayout, QHBoxLayout, QApplication, QPushButton
)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices
import os
import sys

# Posunie base_dir o 2 úrovne vyššie k rootu projektu
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
assets_dir = os.path.join(base_dir, 'Assets')
pictures_dir = os.path.join(assets_dir, 'Pictures')
banners_dir = os.path.join(assets_dir, 'Banners')

image_path = os.path.join(pictures_dir, '1.png')
banner_singleplayer = os.path.join(banners_dir, 'SINGLEPLAYER.png')
banner_console = os.path.join(banners_dir, 'CONSOLE.png')
banner_prisoner = os.path.join(banners_dir, 'PRISONER.png')
banner_flagzones = os.path.join(banners_dir, 'FLAGZONES.png')
banner_supportmywork = os.path.join(banners_dir, 'SUPPORTMYWORK.png')
banner_buymeacoffee = os.path.join(banners_dir, 'BUYMEACOFFEE.png')

MAX_LINES = 64

class App(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SCUM Quality of Life v1.0.3.0 beta")
        self.setMinimumSize(520, 820)
        self.setMaximumSize(520, 820)
        self.setStyleSheet("background-color: #242424;")

        layout = QVBoxLayout()

        # Hlavný obrázok
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignLeft)
        pixmap = QPixmap(image_path)
        if not pixmap.isNull():
            self.image_label.setPixmap(pixmap.scaledToWidth(500))
        else:
            self.image_label.setText("Obrázok sa nepodarilo načítať.")
        layout.addWidget(self.image_label)

        # Banner SINGLEPLAYER
        self.banner1_label = QLabel()
        self.banner1_label.setAlignment(Qt.AlignLeft)
        banner1_pixmap = QPixmap(banner_singleplayer)
        if not banner1_pixmap.isNull():
            self.banner1_label.setPixmap(banner1_pixmap.scaledToWidth(520))
        else:
            self.banner1_label.setText("Banner SINGLEPLAYER sa nepodarilo načítať.")
        layout.addWidget(self.banner1_label)

        # HBox: PRISONER banner + meno
        prisoner_layout = QHBoxLayout()
        self.prisoner_banner = QLabel()
        prisoner_pixmap = QPixmap(banner_prisoner)
        if not prisoner_pixmap.isNull():
            self.prisoner_banner.setPixmap(prisoner_pixmap.scaledToHeight(20, Qt.SmoothTransformation))
        self.prisoner_value = QLabel("Loading...")
        self.prisoner_value.setStyleSheet("font-size:18px; color:#CCCCCC; margin-left:10px;")
        prisoner_layout.addWidget(self.prisoner_banner)
        prisoner_layout.addWidget(self.prisoner_value)
        prisoner_layout.addStretch()
        layout.addLayout(prisoner_layout)

        # HBox: FLAGZONES banner + počet
        flagzones_layout = QHBoxLayout()
        self.flagzones_banner = QLabel()
        flagzones_pixmap = QPixmap(banner_flagzones)
        if not flagzones_pixmap.isNull():
            self.flagzones_banner.setPixmap(flagzones_pixmap.scaledToHeight(20, Qt.SmoothTransformation))
        self.flagzones_value = QLabel("0")
        self.flagzones_value.setStyleSheet("font-size:18px; color:#FF9900; margin-left:10px;")
        flagzones_layout.addWidget(self.flagzones_banner)
        flagzones_layout.addWidget(self.flagzones_value)
        flagzones_layout.addStretch()
        layout.addLayout(flagzones_layout)

        # Banner CONSOLE
        self.banner2_label = QLabel()
        self.banner2_label.setAlignment(Qt.AlignLeft)
        banner2_pixmap = QPixmap(banner_console)
        if not banner2_pixmap.isNull():
            self.banner2_label.setPixmap(banner2_pixmap.scaledToWidth(520))
        else:
            self.banner2_label.setText("Banner CONSOLE sa nepodarilo načítať.")
        layout.addWidget(self.banner2_label)

        # Konzola
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        layout.addWidget(self.console)

        # Banner SUPPORT MY WORK
        self.banner3_label = QLabel()
        self.banner3_label.setAlignment(Qt.AlignLeft)
        banner3_pixmap = QPixmap(banner_supportmywork)
        if not banner3_pixmap.isNull():
            self.banner3_label.setPixmap(banner3_pixmap.scaledToWidth(550))
        else:
            self.banner3_label.setText("Banner SUPPORTMYWORK sa nepodarilo načítať.")
        layout.addWidget(self.banner3_label)

        # HBox: BUYMEACOFFEE banner + tlačidlo
        buyme_layout = QHBoxLayout()
        self.banner4_label = QLabel()
        self.banner4_label.setAlignment(Qt.AlignLeft)
        banner4_pixmap = QPixmap(banner_buymeacoffee)
        if not banner4_pixmap.isNull():
            self.banner4_label.setPixmap(banner4_pixmap.scaledToHeight(28, Qt.SmoothTransformation))
        else:
            self.banner4_label.setText("Banner BUYMEACOFFEE sa nepodarilo načítať.")
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

        # Ukážka
        self.log("SCUM Quality of Life", color="orange")
        self.update_prisoner_name("Name")
        self.update_flag_zones(0)

    def log(self, text, color="#20FF20"):
        current_text = self.console.toHtml()
        new_line = f'<span style="color:{color}">{text}</span><br>'
        self.console.setHtml(current_text + new_line)
        self.console.verticalScrollBar().setValue(self.console.verticalScrollBar().maximum())

    def update_prisoner_name(self, name: str):
        self.prisoner_value.setText(name)

    def update_flag_zones(self, count):
        self.flagzones_value.setText(str(count))

    def open_coffee_link(self):
        url = QUrl("https://www.buymeacoffee.com/jastronit")
        QDesktopServices.openUrl(url)

# Spustenie aplikácie
def run_gui(app: QApplication):
    window = App()
    window.show()
    exitCode = app.exec()
    sys.exit(exitCode)

