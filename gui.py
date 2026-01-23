import math
import os
import sys

from PyQt6.QtCore import QObject, QRect, Qt, QTimer, pyqtSignal
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
    """Animated wave widget for the background."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.phase = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(30)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

    def update_animation(self):
        self.phase += 0.05
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        width = self.width()
        height = self.height()

        # Draw two waves
        self._draw_wave(
            painter, width, height, self.phase, QColor(20, 184, 166, 60), 1.0, 30
        )
        self._draw_wave(
            painter,
            width,
            height,
            self.phase + math.pi * 0.5,
            QColor(20, 184, 166, 110),
            0.7,
            20,
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
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setStyleSheet(
            f"background-color: {BG_COLOR}; color: {TEXT_COLOR}; border: none;"
        )

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # 1. Background Layer: Waves
        self.waves = WaveWidget(self.central_widget)

        # 2. Middle Layer: Content Stack
        self.stack = QStackedWidget(self.central_widget)
        self.stack.setStyleSheet("background: transparent;")

        # 3. Foreground Layer: Overlays
        self._setup_overlays()

        # Initialize Pages
        self.stack.addWidget(self._create_idle_page())
        self.stack.addWidget(self._create_success_page())
        self.stack.addWidget(self._create_error_page())

        self.showFullScreen()

    def _setup_overlays(self):
        # Logo (Top Left)
        logo_path = os.path.join(os.path.dirname(__file__), "assets/images/logo.svg")
        self.logo_widget = QWidget(self.central_widget)
        if os.path.exists(logo_path):
            self.logo_content = QSvgWidget(logo_path, self.logo_widget)
            self.logo_content.setGeometry(0, 0, 80, 80)
        else:
            self.logo_content = QLabel("M", self.logo_widget)
            self.logo_content.setGeometry(0, 0, 80, 80)
            self.logo_content.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.logo_content.setStyleSheet(
                f"background: {ACCENT_COLOR}; border-radius: 12px; font-weight: bold; color: white; font-size: 40px;"
            )

        # Close Button (Top Right)
        self.close_btn = QPushButton("✕", self.central_widget)
        self.close_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent; color: rgba(248, 250, 252, 0.3); font-size: 32px; border-radius: 30px;
            }}
            QPushButton:pressed {{ background: rgba(255, 255, 255, 0.1); color: white; }}
        """)
        self.close_btn.clicked.connect(self.close)

        # Camera Overlay
        self.camera_container = QFrame(self.central_widget)
        self.camera_container.setStyleSheet("background-color: black; border: none;")
        cam_layout = QVBoxLayout(self.camera_container)
        cam_layout.setContentsMargins(0, 0, 0, 0)
        self.camera_label = QLabel()
        self.camera_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.camera_label.setStyleSheet("background: black; border: none;")
        cam_layout.addWidget(self.camera_label)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        w = self.width()
        h = self.height()

        # Position Background Waves
        self.waves.setGeometry(0, h - 180, w, 180)

        # Position Content Stack
        self.stack.setGeometry(0, 0, w, h)

        # Position Overlays
        self.logo_widget.setGeometry(30, 30, 80, 80)
        self.close_btn.setGeometry(w - 90, 30, 60, 60)

        # Reposition Camera to Bottom-Right Corner
        # 180x240 portrait, 20px margin from edges
        self.camera_container.setGeometry(w - 180 - 30, h - 240 - 30, 180, 240)

        # Ensure Z-Order
        self.waves.lower()
        self.logo_widget.raise_()
        self.close_btn.raise_()
        self.camera_container.raise_()

    def _create_idle_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        lbl = QLabel("Bereit zum Scannen")
        lbl.setFont(QFont("Roboto", 56, QFont.Weight.ExtraLight))
        lbl.setStyleSheet("color: white;")

        sub = QLabel("Bitte halten Sie Ihren QR-Code vor die Kamera")
        sub.setFont(QFont("Roboto", 24))
        sub.setStyleSheet("color: rgba(248, 250, 252, 0.5);")

        layout.addStretch(1)
        layout.addWidget(lbl, 0, Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(sub, 0, Qt.AlignmentFlag.AlignCenter)
        layout.addStretch(1)
        return page

    def _create_success_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(100, 140, 100, 100)

        self.success_header = QLabel("Abgabe bestätigt")
        self.success_header.setFont(QFont("Roboto", 42, QFont.Weight.Bold))
        self.success_header.setStyleSheet(
            f"color: {ACCENT_COLOR}; margin-bottom: 20px;"
        )

        self.med_table = QTableWidget()
        self.med_table.setColumnCount(2)
        self.med_table.setHorizontalHeaderLabels(["Medikament", "Menge"])

        h = self.med_table.horizontalHeader()
        h.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        h.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        h.setDefaultAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        )

        self.med_table.setColumnWidth(1, 200)
        self.med_table.setFont(QFont("Roboto", 20))
        self.med_table.verticalHeader().setVisible(False)
        self.med_table.setShowGrid(False)
        self.med_table.setAlternatingRowColors(True)
        self.med_table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        self.med_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        self.med_table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {SURFACE_COLOR}; alternate-background-color: #262f3f;
                color: {TEXT_COLOR}; border-radius: 15px; padding: 10px; outline: none; border: none;
            }}
            QHeaderView::section {{
                background: transparent; color: {ACCENT_COLOR}; padding: 15px; font-weight: bold;
                font-size: 18px; border: none; text-align: left;
            }}
            QTableWidget::item {{ padding: 15px; border-bottom: 1px solid #334155; }}
            QScrollBar:vertical {{ border: none; background: transparent; width: 12px; }}
            QScrollBar::handle:vertical {{ background: rgba(20, 184, 166, 0.3); min-height: 40px; border-radius: 6px; }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; }}
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
        self.error_msg = QLabel("")
        self.error_msg.setFont(QFont("Roboto", 28))
        self.error_msg.setWordWrap(True)
        self.error_msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addStretch(1)
        layout.addWidget(self.error_header, 0, Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.error_msg, 0, Qt.AlignmentFlag.AlignCenter)
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
        items = []
        if isinstance(order, dict):
            items = (
                order.get("medication_items")
                or order.get("prescriptions")
                or order.get("items")
                or []
            )
        elif isinstance(order, list):
            items = order

        self.med_table.setRowCount(0)
        self.med_table.setRowCount(len(items))

        for i, item in enumerate(items):
            med_info = (
                item.get("medication")
                if isinstance(item.get("medication"), dict)
                else item
            )
            name = (
                med_info.get("medication_name") or med_info.get("name") or "Unbekannt"
            )
            qty = item.get("quantity") or item.get("dosage") or "1"
            dosage = f"{qty} Packung" if str(qty).isdigit() else str(qty)

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
            self.med_table.setRowHeight(i, 70)

        self.stack.setCurrentIndex(1)
        QTimer.singleShot(10000, self.display_idle)

    def display_error(self, message):
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
