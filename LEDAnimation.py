import time

from rpi_ws281x import Color, PixelStrip

# PixelStrip initialisieren (wie vorher)
STRIP = PixelStrip(15, 18, 800000, 10, False, 255, 0, ws.WS281_STRIP_GBR)
STRIP.begin()

colors = [LOGO_BLUE, LOGO_TURQUOISE, WHITE]

while True:
    for color in colors:
        for i in range(STRIP.numPixels()):
            STRIP.setPixelColor(i, color)
        STRIP.show()
        time.sleep(1)
s
