import sys

from PyQt6.QtCore import QObject, Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QApplication,
    QFrame,
    QLabel,
    QMainWindow,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)


class MachineSignals(QObject):
    """Signals to update the GUI from other threads (e.g., scanner thread)."""

    show_idle = pyqtSignal()
    show_success = pyqtSignal(dict)
    show_error = pyqtSignal(str)


class MachineGUI(QMainWindow):
    def __init__(self, signals: MachineSignals):
        super().__init__()
        self.signals = signals
        self.init_ui()
        self.connect_signals()

    def init_ui(self):
        # Basic Window Setup
        self.setWindowTitle("MeTIMat Machine Interface")
        self.setStyleSheet("background-color: #FAFAFA;")  # gray-50 from tailwind

        # Main Layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Header (Top Bar) matching frontend design
        self.header = QFrame()
        self.header.setFixedHeight(120)
        self.header.setStyleSheet(
            "background-color: #003366; border-bottom: 4px solid #002244;"
        )  # primary & primary-dark
        header_layout = QVBoxLayout(self.header)
        header_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title = QLabel("MeTIMat")
        title.setFont(QFont("Arial", 42, QFont.Weight.Bold))
        title.setStyleSheet("color: #FFFFFF;")
        header_layout.addWidget(title)

        self.main_layout.addWidget(self.header)

        # Content Stack
        self.stack = QStackedWidget()
        self.main_layout.addWidget(self.stack)

        # 1. Idle Page
        self.idle_page = self._create_page("Bitte QR-Code scannen", "#212121")
        self.stack.addWidget(self.idle_page)

        # 2. Success Page
        self.success_page = QWidget()
        success_layout = QVBoxLayout(self.success_page)
        success_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.success_header = QLabel("Abgabe bestätigt")
        self.success_header.setFont(QFont("Arial", 48, QFont.Weight.Bold))
        self.success_header.setStyleSheet("color: #00694E;")  # success color
        self.success_header.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.order_info = QLabel("")
        self.order_info.setFont(QFont("Arial", 28))
        self.order_info.setStyleSheet("color: #212121; margin: 20px;")
        self.order_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.order_info.setWordWrap(True)

        success_layout.addWidget(self.success_header)
        success_layout.addSpacing(50)
        success_layout.addWidget(self.order_info)
        self.stack.addWidget(self.success_page)

        # 3. Error Page
        self.error_page = QWidget()
        error_layout = QVBoxLayout(self.error_page)
        error_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.error_header = QLabel("Hinweis")
        self.error_header.setFont(QFont("Arial", 48, QFont.Weight.Bold))
        self.error_header.setStyleSheet("color: #D32F2F;")  # error color
        self.error_header.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.error_msg = QLabel("")
        self.error_msg.setFont(QFont("Arial", 28))
        self.error_msg.setStyleSheet("color: #212121; margin: 20px;")
        self.error_msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.error_msg.setWordWrap(True)

        error_layout.addWidget(self.error_header)
        error_layout.addSpacing(50)
        error_layout.addWidget(self.error_msg)
        self.stack.addWidget(self.error_page)

        # Start Fullscreen
        self.showFullScreen()
        # self.setCursor(Qt.CursorShape.BlankCursor) # Enable this for the final machine build

    def _create_page(self, text, color):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label = QLabel(text)
        label.setFont(QFont("Arial", 56, QFont.Weight.Bold))
        label.setStyleSheet(f"color: {color};")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setWordWrap(True)
        layout.addWidget(label)
        return page

    def connect_signals(self):
        self.signals.show_idle.connect(self.display_idle)
        self.signals.show_success.connect(self.display_success)
        self.signals.show_error.connect(self.display_error)

    def display_idle(self):
        self.stack.setCurrentIndex(0)

    def display_success(self, order):
        prescriptions = order.get("prescriptions", [])
        med_names = [p.get("medication_name", "Unbekannt") for p in prescriptions]
        med_str = ", ".join(med_names)

        order_id = order.get("id", "---")
        self.order_info.setText(f"Bestellung #{order_id}\n\nMedikamente:\n{med_str}")
        self.stack.setCurrentIndex(1)
        # Return to idle after 6 seconds
        QTimer.singleShot(6000, self.display_idle)

    def display_error(self, message):
        self.error_msg.setText(message)
        self.stack.setCurrentIndex(2)
        # Return to idle after 6 seconds
        QTimer.singleShot(6000, self.display_idle)


# Global signals object to be imported and used by main script
gui_signals = MachineSignals()


def run_gui_app():
    """Entry point for the GUI process."""
    app = QApplication(sys.argv)
    window = MachineGUI(gui_signals)
    sys.exit(app.exec())


if __name__ == "__main__":
    run_gui_app()
