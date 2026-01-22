import time
from threading import Thread
from typing import Any, List

from rpi_ws281x import RGBW, Color, PixelStrip

from .constants import LED_COUNT, LOGO_BLUE, LOGO_TURQUOISE, STRIP_PARAMETERS


class LEDController(Thread):
    strip: PixelStrip
    color: RGBW
    target_color: RGBW
    timeout: float = 0
    waiting: float = False

    def __init__(self, params: List[Any] = STRIP_PARAMETERS) -> None:
        super().__init__()
        self.strip = PixelStrip(*params)
        self.strip.begin()
        self.color = Color(0, 0, 0)

    def __set_all(self, color: RGBW) -> None:
        for i in range(LED_COUNT):
            self.strip.setPixelColor(i, color)

        self.strip.show()

    def __clear(self):
        for i in range(LED_COUNT):
            self.strip.setPixelColor(i, Color(0, 0, 0))

        self.strip.show()

    def update_color(self, color: RGBW):
        self.color = color

    def run(self):
        last_color = Color(0, 0, 0)

        while True:
            if self.waiting and time.time() - self.timeout > 0:
                self.update_color(self.target_color)
                self.waiting = False

            while self.color == last_color:
                time.sleep(1)

            self.__set_all(self.color)
            last_color = self.color

    def set_timeout(self, timeout: float, color: RGBW):
        self.timeout = time.time() + timeout
        self.waiting = True
        self.target_color = color
