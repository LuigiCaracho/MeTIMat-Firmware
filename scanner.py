import cv2


def scan_camera(camera_id):
    cap = cv2.VideoCapture(camera_id)
    detector = cv2.QRCodeDetector()

    if not cap.isOpened():
        raise RuntimeError("Kamera konnte nicht geöffnet werden")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        data, bbox, _ = detector.detectAndDecode(frame)

        yield data, frame
