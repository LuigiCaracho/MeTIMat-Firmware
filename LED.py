# STRIP = Pixelstrip(15, 18, 800000, 10, False, 255, 0, ws.WS281_STRIP_GBR)
# einzelne LED setzen
def set_led(index, color):
    STRIP.setPixelColor(index, color)
    STRIP.show()


# alle LEDs auf eine Farbe setzen
def set_all(color):
    for i in range(STRIP.numPixels()):
        STRIP.setPixelColor(i, color)
    STRIP.show()


# Farben erstellen
RED = Color(255, 0, 0)
GREEN = Color(0, 255, 0)
BLUE = Color(0, 0, 255)
LOGO_BLUE = Color(0, 102, 204)  # #0066cc
LOGO_TURQUOISE = Color(0, 168, 168)  # #00a8a8
WHITE = Color(255, 255, 255)  # #ffffff

# Beispiel: alle LEDs rot
set_all(RED)
time.sleep(1)
set_all(GREEN)
time.sleep(1)
set_all(BLUE)
