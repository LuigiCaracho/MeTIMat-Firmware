import logging
import os
import subprocess
import threading

import requests
from config import MACHINE_ACCESS_TOKEN
from gui_parts.constants import gui_signals
from led.constants import COLOR_GREEN, COLOR_RED, COLOR_YELLOW
from led.controller import LEDController

# Use simpleaudio for potentially more robust playback on Linux
try:
    import simpleaudio as sa

    HAS_SIMPLEAUDIO = True
except ImportError:
    HAS_SIMPLEAUDIO = False

# Fallback to pygame if simpleaudio is not available
HAS_PYGAME = False
if not HAS_SIMPLEAUDIO:
    try:
        import pygame

        pygame.mixer.init()
        HAS_PYGAME = True
    except ImportError:
        pass

logging.basicConfig(level=logging.INFO)

SOUND_PATH = os.path.join(os.path.dirname(__file__), "assets/sounds/beep.mp3")


def play_beep():
    """
    Plays the scan sound.
    """

    def run_playback():
        logging.info(f"🔊 Attempting to play beep sound from: {SOUND_PATH}")
        if not os.path.exists(SOUND_PATH):
            logging.warning(f"⚠️ Sound file not found: {SOUND_PATH}")
            return

        # Use ffplay with forced direct ALSA output to bypass PulseAudio/Root issues
        # Or try paplay if Pulse is running. We use os.system in a thread to be safe.
        try:
            # Try ffplay with alsa driver directly
            cmd = f"ffplay -nodisp -autoexit -loglevel quiet -driver alsa {SOUND_PATH} > /dev/null 2>&1"
            logging.info(f"🔊 Executing: {cmd}")
            os.system(cmd)
        except Exception as e:
            logging.error(f"❌ Playback thread failed: {e}")

    threading.Thread(target=run_playback, daemon=True).start()


def complete_order(url: str, order_id: int):
    """
    Sends a request to mark the order as completed after dispensing.
    """
    base_url = url.rsplit("/", 1)[0]
    complete_url = f"{base_url}/{order_id}/complete"

    headers = {
        "X-Machine-Token": MACHINE_ACCESS_TOKEN,
        "Content-Type": "application/json",
    }

    try:
        logging.info(f"📤 Completing order #{order_id}...")
        response = requests.post(complete_url, headers=headers, timeout=5)

        if response.status_code == 200:
            logging.info(f"✅ Order #{order_id} successfully marked as completed.")
        else:
            logging.error(
                f"❌ Failed to complete order #{order_id}: {response.status_code}"
            )
    except Exception as e:
        logging.error(f"❌ Completion request failed: {e}")


def send_scan(url: str, qr_data: str, led_controller: LEDController):
    """
    Sends QR data to the validate-qr endpoint with machine authentication.
    Handles the ValidationResponse containing order details and updates LEDs and GUI.
    """

    def post():
        logging.info(f"🔍 send_scan called for data: {qr_data}")
        play_beep()

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

                    prescriptions = order.get("prescriptions", [])
                    medication_items = order.get("medication_items", [])

                    med_names = [
                        p.get("medication_name", "Unknown") for p in prescriptions
                    ]
                    for item in medication_items:
                        med = item.get("medication", {})
                        name = med.get("name", "Unknown")
                        qty = item.get("quantity", 1)
                        med_names.append(f"{name} (x{qty})")

                    logging.info(f"✅ QR valid! Order #{order_id} confirmed.")
                    logging.info(f"📦 Items to dispense: {', '.join(med_names)}")

                    logging.info(data)

                    # Successful scan: Green LED and Success GUI
                    led_controller.set_color(COLOR_GREEN, timeout=10.0)
                    gui_signals.show_success.emit(order)

                    # Simulate dispensing logic
                    logging.info("⚙️ Dispensing medication...")
                    complete_order(url, order_id)
                else:
                    # Invalid code: Red LED and Error GUI
                    message = data.get("message", "Ungültiger Code")
                    logging.warning(f"❌ QR invalid: {qr_data} – {message}")
                    led_controller.set_color(COLOR_RED, timeout=10.0)
                    gui_signals.show_error.emit(message)

            elif response.status_code == 401:
                logging.error("❌ Machine authentication failed (401).")
                led_controller.set_color(COLOR_RED, timeout=3.0)
                gui_signals.show_error.emit("Zugriff verweigert (401)")
            else:
                logging.error(f"❌ API Error {response.status_code}: {response.text}")
                led_controller.set_color(COLOR_RED, timeout=3.0)
                gui_signals.show_error.emit(f"Serverfehler: {response.status_code}")

        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            # Connection issue: Yellow blink LED and Error GUI
            logging.error("❌ Connection error or timeout.")
            led_controller.set_blink(COLOR_YELLOW, duration=3.0)
            gui_signals.show_error.emit("Verbindung zum Server fehlgeschlagen")
        except Exception as e:
            logging.error(f"❌ POST failed: {e}")
            led_controller.set_blink(COLOR_YELLOW, duration=3.0)
            gui_signals.show_error.emit("Ein unerwarteter Fehler ist aufgetreten")

    threading.Thread(target=post, daemon=True).start()
