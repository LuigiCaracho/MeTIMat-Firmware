import logging
import threading

import requests
from config import MACHINE_ACCESS_TOKEN
from led.constants import COLOR_GREEN, COLOR_RED, COLOR_WHITE
from led.controller import LEDController

logging.basicConfig(level=logging.INFO)


def send_scan(url: str, qr_data: str, led_controller: LEDController):
    """
    Sends QR data to the validate-qr endpoint with machine authentication.
    Handles the ValidationResponse containing order details.
    """

    def post():
        # The endpoint expects /api/v1/orders/validate-qr
        # If the provided url is the old /api/scan, we should ideally adjust it
        # but here we assume the passed url is correct or handled by the mock server.

        payload = {"qr_data": qr_data}
        headers = {
            "X-Machine-Token": MACHINE_ACCESS_TOKEN,
            "Content-Type": "application/json",
        }

        try:
            logging.info(f"📤 Sending validation request for: {qr_data}")
            response = requests.post(url, json=payload, headers=headers, timeout=5)

            if response.status_code == 200:
                data = response.json()
                if data.get("valid"):
                    order = data.get("order", {})
                    order_id = order.get("id", "Unknown")

                    # Extract medication names for logging
                    prescriptions = order.get("prescriptions", [])
                    med_names = [
                        p.get("medication_name", "Unknown") for p in prescriptions
                    ]

                    logging.info(f"✅ QR valid! Order #{order_id} confirmed.")
                    logging.info(f"📦 Items to dispense: {', '.join(med_names)}")

                    led_controller.update_color(COLOR_GREEN)
                    led_controller.set_timeout(9, COLOR_WHITE)
                else:
                    message = data.get("message", "Unknown error")
                    logging.warning(f"❌ QR invalid: {qr_data} – {message}")
                    led_controller.update_color(COLOR_RED)
                    led_controller.set_timeout(9, COLOR_WHITE)

            elif response.status_code == 401:
                logging.error(
                    "❌ Machine authentication failed (401). Check MACHINE_ACCESS_TOKEN."
                )
                led_controller.update_color(COLOR_RED)
                led_controller.set_timeout(9, COLOR_WHITE)
            else:
                logging.error(f"❌ API Error {response.status_code}: {response.text}")
                led_controller.update_color(COLOR_RED)
                led_controller.set_timeout(9, COLOR_WHITE)

        except requests.exceptions.Timeout:
            logging.error("❌ Request timed out.")
        except Exception as e:
            logging.error(f"❌ POST failed: {e}")

    threading.Thread(target=post, daemon=True).start()
