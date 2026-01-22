#!/usr/bin/env python3
"""
Main script for client firmware
"""

import cv2
from client import send_scan
from config import API_URL, CAMERA_ID, DUPLICATE_TIMEOUT
from dedup import Deduplicator
from led.controller import LEDController
from scanner import scan_camera


def main():
    dedup = Deduplicator(DUPLICATE_TIMEOUT)
    controller = LEDController()
    controller.start()

    for data, frame in scan_camera(CAMERA_ID):
        if data:
            if dedup.is_new(data):
                print(f"📦 Neuer Scan: {data}")
                send_scan(API_URL, data, controller)

        cv2.imshow("QR Scanner", frame)
        if cv2.waitKey(1) & 0xFF == 27:
            break

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
