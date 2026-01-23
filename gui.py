import math
import os
import sys

from PyQt6.QtCore import QObject, QPointF, Qt, QTimer, pyqtSignal
from PyQt6.QtGui import (
    QColor,
    QFont,
    QImage,
    QPainter,
    QPainterPath,
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
    """Animated wave widget that remains constant at the bottom of the UI."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.phase = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(30)
        self.setFixedHeight(180)

    def update_animation(self):
        self.phase += 0.05
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        width = self.width()
        height = self.height()

        # Draw background waves
        # Back wave
        self._draw_wave(
            painter, width, height, self.phase, QColor(20, 184, 166, 60), 1.0, 30
        )
        # Front wave
        self._draw_wave(
            painter,
            width,
            height,
            self.phase + math.pi * 0.5,
            QColor(20, 184, 166, 120),
            0.7,
            25,
        )

    def _draw_wave(self, painter, w, h, phase, color, frequency, amplitude):
        path = QPainterPath()
        path.moveTo(0, h)
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
        # Window Setup
        self.setWindowTitle("MeTIMat Machine Interface")
        self.setFixedSize(1280, 720)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setStyleSheet(
            f"background-color: {BG_COLOR}; color: {TEXT_COLOR}; border: none;"
        )

        # Main Container
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Background Layer: Stack + Waves
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.stack = QStackedWidget()
        self.stack.setStyleSheet("background: transparent;")
        self.main_layout.addWidget(self.stack, 1)

        self.waves = WaveWidget()
        self.main_layout.addWidget(self.waves)

        # Foreground Overlays (Logo, Close, Camera)
        self._setup_overlays()

        # Initialize Pages
        self.stack.addWidget(self._create_idle_page())
        self.stack.addWidget(self._create_success_page())
        self.stack.addWidget(self._create_error_page())

        self.show()

    def _setup_overlays(self):
        # Logo (Top Left, Square 80x80)
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
        self.close_btn.setGeometry(1180, 30, 70, 70)
        self.close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.close_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: rgba(248, 250, 252, 0.4);
                font-size: 36px;
                border-radius: 35px;
            }}
            QPushButton:pressed {{
                background-color: rgba(255, 255, 255, 0.1);
            }}
        """)
        self.close_btn.clicked.connect(self.close)
        self.close_btn.raise_()

        # Camera Overlay Container (Bottom Right)
        self.camera_container = QFrame(self.central_widget)
        self.camera_container.setGeometry(920, 420, 320, 240)
        self.camera_container.setStyleSheet(f"""
            QFrame {{
                border: 2px solid {ACCENT_COLOR};
                background-color: black;
                border-radius: 16px;
            }}
        """)

        cam_layout = QVBoxLayout(self.camera_container)
        cam_layout.setContentsMargins(2, 2, 2, 2)
        self.camera_label = QLabel()
        self.camera_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.camera_label.setStyleSheet("border-radius: 14px; background: black;")
        cam_layout.addWidget(self.camera_label)
        self.camera_container.raise_()

    def _create_idle_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        label = QLabel("Bereit zum Scannen")
        label.setFont(QFont("Roboto", 56, QFont.Weight.ExtraLight))
        label.setStyleSheet("margin-bottom: 10px;")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        sub_label = QLabel("Bitte halten Sie Ihren QR-Code vor die Kamera")
        sub_label.setFont(QFont("Roboto", 24))
        sub_label.setStyleSheet("color: rgba(248, 250, 252, 0.6);")
        sub_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addStretch(1)
        layout.addWidget(label)
        layout.addWidget(sub_label)
        layout.addStretch(1)
        return page

    def _create_success_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(100, 120, 100, 20)

        self.success_header = QLabel("Abgabe bestätigt")
        self.success_header.setFont(QFont("Roboto", 42, QFont.Weight.Bold))
        self.success_header.setStyleSheet(
            f"color: {ACCENT_COLOR}; margin-bottom: 30px;"
        )

        self.med_table = QTableWidget()
        self.med_table.setColumnCount(2)
        self.med_table.setHorizontalHeaderLabels(["Medikament", "Menge"])

        header = self.med_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        header.setDefaultAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        )

        self.med_table.setColumnWidth(1, 220)
        self.med_table.setFont(QFont("Roboto", 20))
        self.med_table.verticalHeader().setVisible(False)
        self.med_table.setShowGrid(False)
        self.med_table.setAlternatingRowColors(True)
        self.med_table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        self.med_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        self.med_table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {SURFACE_COLOR};
                alternate-background-color: #262f3f;
                color: {TEXT_COLOR};
                gridline-color: transparent;
                border-radius: 20px;
                padding: 10px;
                outline: none;
            }}
            QHeaderView::section {{
                background-color: transparent;
                color: {ACCENT_COLOR};
                padding: 15px;
                font-weight: bold;
                border: none;
                font-size: 18px;
                text-transform: uppercase;
                letter-spacing: 1px;
                text-align: left;
            }}
            QTableWidget::item {{
                padding: 15px;
                border-bottom: 1px solid #334155;
            }}
        """)

        layout.addWidget(self.success_header)
        layout.addWidget(self.med_table)
        layout.addStretch(1)
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
        self.error_msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.error_msg.setWordWrap(True)

        layout.addStretch(1)
        layout.addWidget(self.error_header)
        layout.addWidget(self.error_msg)
        layout.addStretch(1)
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

        self.med_table.setRowCount(0)
        self.med_table.setRowCount(len(prescriptions))

        for i, p in enumerate(prescriptions):
            name = p.get("medication_name") or p.get("name") or "Unbekannt"
            dosage = "1 Packung"

            item_name = QTableWidgetItem(name)
            item_dosage = QTableWidgetItem(dosage)

            item_name.setForeground(QColor(TEXT_COLOR))
            item_dosage.setForeground(QColor(TEXT_COLOR))

            item_name.setTextAlignment(
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
            )
            item_dosage.setTextAlignment(
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
            )

            self.med_table.setItem(i, 0, item_name)
            self.med_table.setItem(i, 1, item_dosage)
            self.med_table.setRowHeight(i, 80)

        QTimer.singleShot(10000, self.display_idle)

    def display_error(self, message):
        if any(x in message for x in ["Verbindung", "401", "Server"]):
            self.error_header.setText("Verbindungsfehler")
        else:
            self.error_header.setText("Ungültiger Code")
        self.error_msg.setText(message)
        self.stack.setCurrentIndex(2)
        QTimer.singleShot(6000, self.display_idle)


gui_signals = MachineSignals()


def run_gui_app():
    app = QApplication(sys.argv)
    window = MachineGUI(gui_signals)
    sys.exit(app.exec())


if __name__ == "__main__":
    run_gui_app()
