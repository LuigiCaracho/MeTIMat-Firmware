#!/usr/bin/env python3
"""
Main script for client firmware integrating LED control, QR scanning, and GUI.
"""

import sys
import threading

import cv2
from client import send_scan
from config import API_URL, CAMERA_ID, DUPLICATE_TIMEOUT
from dedup import Deduplicator
from gui import MachineGUI
from gui_parts.constants import gui_signals
from led.controller import LEDController
from PyQt6.QtGui import QImage
from PyQt6.QtWidgets import QApplication
from scanner import scan_camera


def scanner_worker(led_controller):
    """
    Background worker for QR code scanning and camera feed updates.
    """
    dedup = Deduplicator(DUPLICATE_TIMEOUT)

    while True:
        try:
            for data, frame in scan_camera(CAMERA_ID):
                # 1. Update GUI Camera Feed
                if frame is not None:
                    # Convert BGR (OpenCV) to RGB (Qt)
                    rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    h, w, ch = rgb_image.shape
                    bytes_per_line = ch * w
                    qt_image = QImage(
                        rgb_image.data,
                        w,
                        h,
                        bytes_per_line,
                        QImage.Format.Format_RGB888,
                    )
                    # Emit signal to update GUI in main thread
                    gui_signals.update_frame.emit(qt_image)

                # 2. Process QR Data
                if data:
                    if dedup.is_new(data):
                        print(f"📦 Neuer Scan: {data}")
                        send_scan(API_URL, data, led_controller)

        except Exception as e:
            print(f"Scanner Error: {e}")
            continue


def main():
    # 1. Initialize LED Controller
    controller = LEDController()
    controller.start()
    controller.set_idle()

    # 2. Start Scanner Thread
    scan_thread = threading.Thread(
        target=scanner_worker, args=(controller,), daemon=True
    )
    scan_thread.start()

    # 3. Launch GUI (Main Thread)
    app = QApplication(sys.argv)
    _ = MachineGUI(gui_signals)

    # Run the application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
