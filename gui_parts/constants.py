from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QImage

# Theme Colors
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


# Global signals instance
gui_signals = MachineSignals()
