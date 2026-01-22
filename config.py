API_HOST = "127.0.0.1"
API_LISTEN_HOST = "0.0.0.0"
API_PORT = 5000
API_PATH = "/api/v1/orders/validate-qr"

API_URL = f"http://{API_HOST}:{API_PORT}/{API_PATH.strip('/')}"
DUPLICATE_TIMEOUT = 5  # Sekunden
CAMERA_ID = 0
MACHINE_ACCESS_TOKEN = "your-machine-token-here"
