import math
import os
import sys

from PyQt6.QtCore import QObject, QPointF, QRectF, QSize, Qt, QTimer, pyqtSignal
from PyQt6.QtGui import (
    QColor,
    QFont,
    QIcon,
    QImage,
    QPainter,
    QPainterPath,
    QPen,
    QPixmap,
)
from PyQt6.QtSvgWidgets import QSvgWidget
from PyQt6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

# Constants for the theme
BG_COLOR = "#1e3a8a"  # Deep Blue
ACCENT_COLOR = "#14b8a6"  # Teal
TEXT_COLOR = "#f8fafc"  # Slate 50
SURFACE_COLOR = "#1e293b"  # Slate 800
ERROR_COLOR = "#ef4444"  # Red-500


class MachineSignals(QObject):
    """Signals to update the GUI from other threads."""

    show_idle = pyqtSignal()
    show_success = pyqtSignal(dict)
    show_error = pyqtSignal(str)
    update_frame = pyqtSignal(QImage)


class WaveWidget(QWidget):
    """Animated wave widget for the idle state."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.phase = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(30)
        self.setFixedHeight(150)

    def update_animation(self):
        self.phase += 0.05
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        width = self.width()
        height = self.height()

        # Draw two waves with different phases/opacities
        self._draw_wave(
            painter, width, height, self.phase, QColor(20, 184, 166, 80), 1.0
        )
        self._draw_wave(
            painter,
            width,
            height,
            self.phase + math.pi * 0.5,
            QColor(20, 184, 166, 150),
            0.7,
        )

    def _draw_wave(self, painter, w, h, phase, color, frequency):
        path = QPainterPath()
        path.moveTo(0, h)

        amplitude = 25
        mid_y = h / 2

        for x in range(0, w + 1, 5):
            y = mid_y + math.sin(x * 0.008 * frequency + phase) * amplitude
            path.lineTo(float(x), y)

        path.lineTo(w, h)
        path.closeSubpath()

        painter.fillPath(path, color)


class MachineGUI(QMainWindow):
    def __init__(self, signals: MachineSignals):
        super().__init__()
        self.signals = signals
        self.init_ui()
        self.connect_signals()

    def init_ui(self):
        # Basic Window Setup
        self.setWindowTitle("MeTIMat Machine Interface")
        self.setFixedSize(1280, 720)  # 720p 16:9
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setStyleSheet(
            f"background-color: {BG_COLOR}; color: {TEXT_COLOR}; border: none;"
        )

        # Main Layout Container
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.root_layout = QVBoxLayout(self.central_widget)
        self.root_layout.setContentsMargins(0, 0, 0, 0)
        self.root_layout.setSpacing(0)

        # 1. Overlay Elements (Logo, Close, Camera)
        self._setup_overlays()

        # 2. Main Content Stack
        self.stack = QStackedWidget()
        self.root_layout.addWidget(self.stack)

        # -- Idle Page --
        self.idle_page = self._create_idle_page()
        self.stack.addWidget(self.idle_page)

        # -- Success Page (Table) --
        self.success_page = self._create_success_page()
        self.stack.addWidget(self.success_page)

        # -- Error Page --
        self.error_page = self._create_error_page()
        self.stack.addWidget(self.error_page)

        self.show()

    def _setup_overlays(self):
        # Logo (Top Left, Explicitly Square 80x80)
        logo_path = os.path.join(os.path.dirname(__file__), "assets/images/logo.svg")
        if os.path.exists(logo_path):
            self.logo_widget = QSvgWidget(logo_path, self.central_widget)
            self.logo_widget.setGeometry(40, 40, 80, 80)
        else:
            self.logo_placeholder = QLabel("M", self.central_widget)
            self.logo_placeholder.setGeometry(40, 40, 80, 80)
            self.logo_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.logo_placeholder.setFont(QFont("Roboto", 32, QFont.Weight.Bold))
            self.logo_placeholder.setStyleSheet(
                f"background-color: {ACCENT_COLOR}; border-radius: 12px; color: white;"
            )

        # Close Button (Top Right)
        self.close_btn = QPushButton("✕", self.central_widget)
        self.close_btn.setGeometry(1200, 20, 60, 60)
        self.close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.close_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: rgba(248, 250, 252, 0.5);
                font-size: 28px;
                border-radius: 30px;
            }}
            QPushButton:hover {{
                color: {TEXT_COLOR};
                background-color: rgba(255, 255, 255, 0.1);
            }}
        """)
        self.close_btn.clicked.connect(self.close)

        # Camera Overlay (Bottom Right)
        self.camera_container = QFrame(self.central_widget)
        self.camera_container.setGeometry(920, 440, 320, 240)
        self.camera_container.setStyleSheet(f"""
            QFrame {{
                border: 2px solid {ACCENT_COLOR};
                background-color: black;
                border-radius: 16px;
            }}
        """)

        camera_layout = QVBoxLayout(self.camera_container)
        camera_layout.setContentsMargins(2, 2, 2, 2)

        self.camera_label = QLabel()
        self.camera_label.setStyleSheet("border-radius: 14px; background-color: black;")
        self.camera_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        camera_layout.addWidget(self.camera_label)

    def _create_idle_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)

        content_vbox = QVBoxLayout()
        content_vbox.setAlignment(Qt.AlignmentFlag.AlignCenter)

        label = QLabel("Bereit zum Scannen")
        label.setFont(QFont("Roboto", 52, QFont.Weight.ExtraLight))
        label.setStyleSheet(f"color: {TEXT_COLOR}; margin-bottom: 10px;")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        sub_label = QLabel("Bitte halten Sie Ihren QR-Code vor die Kamera")
        sub_label.setFont(QFont("Roboto", 22))
        sub_label.setStyleSheet("color: rgba(248, 250, 252, 0.6);")
        sub_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        content_vbox.addWidget(label)
        content_vbox.addWidget(sub_label)

        layout.addStretch(1)
        layout.addLayout(content_vbox)
        layout.addStretch(1)

        # Wave Animation at the bottom
        self.waves = WaveWidget()
        layout.addWidget(self.waves)

        return page

    def _create_success_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(100, 120, 100, 100)

        self.success_header = QLabel("Abgabe bestätigt")
        self.success_header.setFont(QFont("Roboto", 42, QFont.Weight.Bold))
        self.success_header.setStyleSheet(
            f"color: {ACCENT_COLOR}; margin-bottom: 30px;"
        )

        self.med_table = QTableWidget()
        self.med_table.setColumnCount(2)
        self.med_table.setHorizontalHeaderLabels(["Medikament", "Menge"])
        self.med_table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch
        )
        self.med_table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Fixed
        )
        self.med_table.setColumnWidth(1, 180)
        self.med_table.setFont(QFont("Roboto", 20))
        self.med_table.setShowGrid(False)
        self.med_table.setAlternatingRowColors(True)
        self.med_table.verticalHeader().setVisible(False)
        self.med_table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        self.med_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        self.med_table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {SURFACE_COLOR};
                alternate-background-color: #262f3f;
                color: {TEXT_COLOR};
                gridline-color: transparent;
                border-radius: 20px;
                padding: 15px;
                outline: none;
            }}
            QHeaderView::section {{
                background-color: transparent;
                color: {ACCENT_COLOR};
                padding: 20px;
                font-weight: bold;
                border: none;
                font-size: 18px;
                text-transform: uppercase;
                letter-spacing: 1px;
            }}
            QTableWidget::item {{
                padding: 20px;
                border-bottom: 1px solid #334155;
            }}
        """)

        layout.addWidget(self.success_header)
        layout.addWidget(self.med_table)
        return page

    def _create_error_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.error_header = QLabel("Fehler")
        self.error_header.setFont(QFont("Roboto", 56, QFont.Weight.Bold))
        self.error_header.setStyleSheet(f"color: {ERROR_COLOR};")
        self.error_header.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.error_msg = QLabel("")
        self.error_msg.setFont(QFont("Roboto", 28))
        self.error_msg.setStyleSheet(f"color: {TEXT_COLOR}; margin: 40px;")
        self.error_msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.error_msg.setWordWrap(True)

        layout.addWidget(self.error_header)
        layout.addWidget(self.error_msg)
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
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
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
            dosage = "1 Packung"  # Mock dosage if not provided

            item_name = QTableWidgetItem(name)
            item_dosage = QTableWidgetItem(dosage)

            item_name.setTextAlignment(
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
            )
            item_dosage.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            self.med_table.setItem(i, 0, item_name)
            self.med_table.setItem(i, 1, item_dosage)

        QTimer.singleShot(8000, self.display_idle)

    def display_error(self, message):
        if "Verbindung" in message or "401" in message or "Server" in message:
            self.error_header.setText("Verbindungsfehler")
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
