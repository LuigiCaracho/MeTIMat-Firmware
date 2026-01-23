import os
import sys

import cv2
from PyQt6.QtCore import QObject, QSize, Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QImage, QPixmap
from PyQt6.QtSvgWidgets import QSvgWidget
from PyQt6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMainWindow,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


class MachineSignals(QObject):
    """Signals to update the GUI from other threads."""

    show_idle = pyqtSignal()
    show_success = pyqtSignal(dict)
    show_error = pyqtSignal(str)
    update_frame = pyqtSignal(QImage)


class MachineGUI(QMainWindow):
    def __init__(self, signals: MachineSignals):
        super().__init__()
        self.signals = signals
        self.init_ui()
        self.connect_signals()

    def init_ui(self):
        # Basic Window Setup
        self.setWindowTitle("MeTIMat Machine Interface")
        self.setStyleSheet("background-color: #FAFAFA;")  # gray-50

        # Main Layout Container
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.root_layout = QVBoxLayout(self.central_widget)
        self.root_layout.setContentsMargins(0, 0, 0, 0)
        self.root_layout.setSpacing(0)

        # 1. Header with Logo
        self.header = QFrame()
        self.header.setFixedHeight(140)
        self.header.setStyleSheet(
            "background-color: #003366; border-bottom: 4px solid #002244;"
        )
        header_layout = QHBoxLayout(self.header)
        header_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        logo_path = os.path.join(os.path.dirname(__file__), "assets/images/logo.svg")
        if os.path.exists(logo_path):
            self.logo_widget = QSvgWidget(logo_path)
            self.logo_widget.setFixedSize(250, 100)
            header_layout.addWidget(self.logo_widget)
        self.root_layout.addWidget(self.header)

        # 2. Main Content Stack
        self.content_container = QWidget()
        self.content_layout = QVBoxLayout(self.content_container)
        self.root_layout.addWidget(self.content_container, 1)

        self.stack = QStackedWidget()
        self.content_layout.addWidget(self.stack)

        # -- Idle Page --
        self.idle_page = self._create_page("Bitte QR-Code scannen", "#212121")
        self.stack.addWidget(self.idle_page)

        # -- Success Page (Table) --
        self.success_page = QWidget()
        success_vbox = QVBoxLayout(self.success_page)

        self.success_header = QLabel("Abgabe bestätigt")
        self.success_header.setFont(QFont("Arial", 42, QFont.Weight.Bold))
        self.success_header.setStyleSheet("color: #00694E; margin-top: 20px;")
        self.success_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        success_vbox.addWidget(self.success_header)

        self.med_table = QTableWidget()
        self.med_table.setColumnCount(2)
        self.med_table.setHorizontalHeaderLabels(["Medikament", "Menge"])
        self.med_table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch
        )
        self.med_table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Fixed
        )
        self.med_table.setColumnWidth(1, 150)
        self.med_table.setFont(QFont("Arial", 20))
        self.med_table.setStyleSheet("""
            QTableWidget { background-color: white; border: 1px solid #E0E0E0; gridline-color: #E0E0E0; }
            QHeaderView::section { background-color: #F5F5F5; padding: 10px; font-weight: bold; border: none; border-bottom: 2px solid #003366; }
        """)
        success_vbox.addWidget(self.med_table)
        self.stack.addWidget(self.success_page)

        # -- Error Page --
        self.error_page = QWidget()
        error_vbox = QVBoxLayout(self.error_page)
        error_vbox.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.error_header = QLabel("Fehler")
        self.error_header.setFont(QFont("Arial", 42, QFont.Weight.Bold))
        self.error_header.setStyleSheet("color: #D32F2F;")
        self.error_header.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.error_msg = QLabel("")
        self.error_msg.setFont(QFont("Arial", 32))
        self.error_msg.setStyleSheet("color: #212121; margin: 40px;")
        self.error_msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.error_msg.setWordWrap(True)

        error_vbox.addWidget(self.error_header)
        error_vbox.addWidget(self.error_msg)
        self.stack.addWidget(self.error_page)

        # 3. Camera Overlay (Bottom Right)
        self.camera_label = QLabel(self.central_widget)
        self.camera_label.setFixedSize(320, 240)
        self.camera_label.setStyleSheet(
            "border: 4px solid #003366; background-color: black;"
        )
        self.camera_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Position camera in bottom right using resizeEvent or just fixed move for now
        # We will update position in resizeEvent

        self.showFullScreen()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Move camera to bottom right
        margin = 20
        self.camera_label.move(
            self.width() - self.camera_label.width() - margin,
            self.height() - self.camera_label.height() - margin,
        )

    def _create_page(self, text, color):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label = QLabel(text)
        label.setFont(QFont("Arial", 52, QFont.Weight.Bold))
        label.setStyleSheet(f"color: {color};")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        return page

    def connect_signals(self):
        self.signals.show_idle.connect(self.display_idle)
        self.signals.show_success.connect(self.display_success)
        self.signals.show_error.connect(self.display_error)
        self.signals.update_frame.connect(self.set_camera_frame)

    def set_camera_frame(self, image):
        self.camera_label.setPixmap(
            QPixmap.fromImage(image).scaled(
                self.camera_label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )

    def display_idle(self):
        self.stack.setCurrentIndex(0)

    def display_success(self, order):
        self.stack.setCurrentIndex(1)
        prescriptions = order.get("prescriptions", [])
        self.med_table.setRowCount(len(prescriptions))

        for i, p in enumerate(prescriptions):
            name = p.get("medication_name", "Unbekannt")
            dosage = p.get("dosage", "1")

            item_name = QTableWidgetItem(name)
            item_dosage = QTableWidgetItem(str(dosage))

            item_name.setTextAlignment(
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
            )
            item_dosage.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            self.med_table.setItem(i, 0, item_name)
            self.med_table.setItem(i, 1, item_dosage)

        QTimer.singleShot(8000, self.display_idle)

    def display_error(self, message):
        # Determine if it's a network error or invalid code
        if "Verbindung" in message or "401" in message or "Server" in message:
            self.error_header.setText("Netzwerkfehler")
        else:
            self.error_header.setText("Ungültiger Code")

        self.error_msg.setText(message)
        self.stack.setCurrentIndex(2)
        QTimer.singleShot(6000, self.display_idle)


# Global signals
gui_signals = MachineSignals()


def run_gui_app():
    app = QApplication(sys.argv)
    window = MachineGUI(gui_signals)
    sys.exit(app.exec())


if __name__ == "__main__":
    run_gui_app()
