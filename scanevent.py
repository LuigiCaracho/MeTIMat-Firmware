import os
import sys
import threading
import time

import config  # Keeping this import as it was in the original file

# Add the parent directory to the Python path to allow importing 'led'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import necessary components from the led module
from rpi_ws281x import Color

from led.controller import LEDController


class ScanEvent:
    def __init__(self):
        # Initialize LEDController and start its internal thread
        self.led_controller = LEDController()
        self.led_controller.start()

    def handle_scan(self, qr_code_data):
        """
        Handles a QR code scan event.
        If the QR code data is 'valid_qr_code', it turns on a green LED for 10 seconds.
        """
        print(f"Scanned QR Code Data: {qr_code_data}")

        if self._is_valid_qr(qr_code_data):
            print("Valid QR code detected! Activating green LED for 10 seconds.")
            # Start a new thread for LED control to avoid blocking the main scan loop
            led_thread = threading.Thread(
                target=self._activate_green_led_for_duration, args=(10,)
            )
            led_thread.start()
        else:
            print("Invalid QR code.")

    def _is_valid_qr(self, qr_code_data):
        """
        Placeholder for QR code validation logic.
        For demonstration, 'valid_qr_code' is considered valid.
        """
        return qr_code_data == "valid_qr_code"

    def _activate_green_led_for_duration(self, duration):
        """
        Activates the green LED for a specified duration using the LEDController's update_color method.
        """
        # Define green color using rpi_ws281x.Color format (RGB)
        green_color = Color(0, 255, 0)
        off_color = Color(0, 0, 0)

        try:
            print(f"Green LED ON for {duration} seconds.")
            self.led_controller.update_color(green_color)
            time.sleep(duration)
            self.led_controller.update_color(off_color)
            print("Green LED OFF.")
        except AttributeError:
            print(
                "LEDController.update_color method might not be implemented as expected. Using placeholder behavior."
            )
            # Fallback to placeholder if actual LED methods don't exist
            self.led_controller.update_color(green_color)
            time.sleep(duration)
            self.led_controller.update_color(off_color)


def simulate_scan_events():
    """
    Simulates continuous scanning of QR codes.
    """
    scanner = ScanEvent()
    print(
        "Simulating QR code scanning. Type 'valid' for a valid QR code, or anything else for invalid. Type 'exit' to quit."
    )
    while True:
        user_input = input("Enter QR code data: ").strip()
        if user_input.lower() == "exit":
            print("Exiting scanner simulation.")
            break
        elif user_input.lower() == "valid":
            scanner.handle_scan("valid_qr_code")
        else:
            scanner.handle_scan(user_input)


if __name__ == "__main__":
    simulate_scan_events()
