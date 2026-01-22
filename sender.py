import logging
import threading

import requests

logging.basicConfig(level=logging.INFO)


def send_scan(url, qr_data):
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
                else:
                    logging.warning(
                        f"❌ QR ungültig: {qr_data} – Message: {data.get('message')}"
                    )
            else:
                logging.error(f"❌ POST {response.status_code}: {qr_data}")
        except Exception as e:
            logging.error(f"❌ POST fehlgeschlagen: {e}")

    threading.Thread(target=post, daemon=True).start()
