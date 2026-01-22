#!/usr/bin/env python3
"""
Run idle animation
"""

import time

from led.constants import LOGO_BLUE, LOGO_TURQUOISE
from led.controller import LEDController

if __name__ == "__main__":
    controller = LEDController()
    controller.start()

    while True:
        controller.update_color(LOGO_TURQUOISE)
        time.sleep(1)
        controller.update_color(LOGO_BLUE)
        time.sleep(1)
