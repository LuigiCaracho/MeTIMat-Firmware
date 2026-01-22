import cv2

from config import API_URL, CAMERA_ID, DUPLICATE_TIMEOUT
from dedup import Deduplicator
from scanner import scan_camera
from sender import send_scan


def main():
    dedup = Deduplicator(DUPLICATE_TIMEOUT)

    for data, frame in scan_camera(CAMERA_ID):
        if data:
            if dedup.is_new(data):
                print(f"📦 Neuer Scan: {data}")
                send_scan(API_URL, data)
            else:
                print("🔁 Duplikat ignoriert")

        cv2.imshow("QR Scanner", frame)
        if cv2.waitKey(1) & 0xFF == 27:
            break

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
