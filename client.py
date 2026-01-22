import logging
import os
import sys
import threading
import time

import requests

from led.constants import GREEN, RED, WHITE
from led.controller import LEDController

logging.basicConfig(level=logging.INFO)


def send_scan(url: str, qr_data: str, led_controller: LEDController):
    """
    Sendet QR-Code an API, prüft Response nach QRValidationResponse-Format
    """

    def post():
        payload = {"qr_data": qr_data}
        try:
            response = requests.post(url, json=payload, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get("valid"):
                    logging.info(
                        f"✅ QR gültig: {qr_data} – Profile: {data.get('profile')}"
                    )
                    led_controller.update_color(GREEN)
                    led_controller.set_timeout(9, WHITE)
                else:
                    logging.warning(
                        f"❌ QR ungültig: {qr_data} – Message: {data.get('message')}"
                    )
                    led_controller.update_color(RED)
                    led_controller.set_timeout(9, WHITE)

            else:
                logging.error(f"❌ POST {response.status_code}: {qr_data}")
        except Exception as e:
            logging.error(f"❌ POST fehlgeschlagen: {e}")

    threading.Thread(target=post, daemon=True).start()
