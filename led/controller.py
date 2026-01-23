import time
from threading import Thread
from typing import Any, List, Tuple

from rpi_ws281x import Color, PixelStrip

from .constants import (
    COLOR_LOGO_BLUE,
    COLOR_LOGO_TURQUOISE,
    COLOR_WHITE,
    COLOR_YELLOW,
    LED_COUNT,
    STRIP_PARAMETERS,
)


class LEDController(Thread):
    def __init__(self, params: List[Any] = STRIP_PARAMETERS) -> None:
        super().__init__()
        self.strip = PixelStrip(*params)
        self.strip.begin()

        # State management
        self.mode = "idle"  # idle, solid, blink
        self.current_color = (0, 0, 0)
        self.target_color = (0, 0, 0)

        # Animation variables
        self.idle_colors = [
            (255, 255, 255),  # COLOR_WHITE
            (0, 102, 204),  # COLOR_LOGO_BLUE
            (0, 168, 168),  # COLOR_LOGO_TURQUOISE
        ]
        self.idle_index = 0
        self.transition_start_time = time.time()
        self.transition_duration = 3.0  # seconds per transition

        self.blink_color = (255, 255, 0)
        self.blink_end_time = 0
        self.blink_state = False
        self.last_blink_toggle = 0

        self.timeout_time = 0
        self.daemon = True

    def _get_rgb(self, color_int: int) -> Tuple[int, int, int]:
        return (color_int >> 16) & 0xFF, (color_int >> 8) & 0xFF, color_int & 0xFF

    def _set_all(self, r: int, g: int, b: int):
        color = Color(int(r), int(g), int(b))
        for i in range(LED_COUNT):
            self.strip.setPixelColor(i, color)
        self.strip.show()

    def _interpolate(
        self, start: Tuple[int, int, int], end: Tuple[int, int, int], progress: float
    ) -> Tuple[int, int, int]:
        return (
            int(start[0] + (end[0] - start[0]) * progress),
            int(start[1] + (end[1] - start[1]) * progress),
            int(start[2] + (end[2] - start[2]) * progress),
        )

    def set_idle(self):
        self.mode = "idle"
        self.transition_start_time = time.time()

    def set_color(self, color_int: int, timeout: float = 0):
        self.mode = "solid"
        self.target_color = self._get_rgb(color_int)
        if timeout > 0:
            self.timeout_time = time.time() + timeout
        else:
            self.timeout_time = 0

    def set_blink(self, color_int: int, duration: float):
        self.mode = "blink"
        self.blink_color = self._get_rgb(color_int)
        self.blink_end_time = time.time() + duration
        self.last_blink_toggle = time.time()
        self.blink_state = True

    def run(self):
        while True:
            now = time.time()

            if self.mode == "idle":
                # Smooth transition between idle colors
                elapsed = (now - self.transition_start_time) % (
                    self.transition_duration * len(self.idle_colors)
                )
                self.idle_index = int(elapsed // self.transition_duration)
                progress = (
                    elapsed % self.transition_duration
                ) / self.transition_duration

                start_c = self.idle_colors[self.idle_index]
                end_c = self.idle_colors[(self.idle_index + 1) % len(self.idle_colors)]

                r, g, b = self._interpolate(start_c, end_c, progress)
                self._set_all(r, g, b)

            elif self.mode == "blink":
                if now > self.blink_end_time:
                    self.set_idle()
                    continue

                if now - self.last_blink_toggle > 0.3:  # 300ms blink rate
                    self.blink_state = not self.blink_state
                    self.last_blink_toggle = now

                if self.blink_state:
                    self._set_all(*self.blink_color)
                else:
                    self._set_all(0, 0, 0)

            elif self.mode == "solid":
                if self.timeout_time > 0 and now > self.timeout_time:
                    self.set_idle()
                    continue
                self._set_all(*self.target_color)

            time.sleep(0.05)
