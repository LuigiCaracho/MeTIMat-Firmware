import cv2
from pyzbar import pyzbar


def main():
    # Kamera öffnen (0 = Standard-Webcam)
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("❌ Kamera konnte nicht geöffnet werden")
        return

    print("📷 Kamera läuft – QR-/Barcodes werden gescannt (ESC zum Beenden)")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ Kein Kamerabild")
            break

        # Codes im Bild erkennen
        codes = pyzbar.decode(frame)

        for code in codes:
            data = code.data.decode("utf-8")
            code_type = code.type
            print(f"📦 Gefunden [{code_type}]: {data}")

            # Rechteck um den Code zeichnen
            x, y, w, h = code.rect
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(
                frame, data, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2
            )

        # Bild anzeigen
        cv2.imshow("Kamera Scanner", frame)

        # ESC zum Beenden
        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
