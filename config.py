import os
import shutil
from pathlib import Path

from dotenv import load_dotenv

# Path to the .env and env.example files
base_path = Path(__file__).parent
env_path = base_path / ".env"
example_path = base_path / "env.example"

# Automatically create .env from env.example if it doesn't exist
if not env_path.exists() and example_path.exists():
    shutil.copy(example_path, env_path)
    print(f"Created {env_path} from {example_path}")

# Load environment variables from .env file
load_dotenv(dotenv_path=env_path)

# API Configuration (Remote Backend)
API_HOST = os.getenv("API_HOST", "app.metimat.de")
API_PORT = int(os.getenv("API_PORT", "443"))
API_USE_SSL = os.getenv("API_USE_SSL", "True").lower() == "true"
API_PATH = os.getenv("API_PATH", "/api/v1/orders/validate-qr")

# Local Listener Settings
API_LISTEN_HOST = os.getenv("API_LISTEN_HOST", "0.0.0.0")
API_LISTEN_PORT = int(os.getenv("API_LISTEN_PORT", "8001"))

# Construct API URL
protocol = "https" if API_USE_SSL else "http"
API_URL = f"{protocol}://{API_HOST}:{API_PORT}/{API_PATH.lstrip('/')}"

# Hardware & Timeout Settings
DUPLICATE_TIMEOUT = int(os.getenv("DUPLICATE_TIMEOUT", "5"))
CAMERA_ID = int(os.getenv("CAMERA_ID", "0"))

# Secrets
# This key must match the 'validation_key' for this location in the backend database
MACHINE_ACCESS_TOKEN = os.getenv(
    "MACHINE_ACCESS_TOKEN",
    "1l8uu8F2ZeZk2skuB0sWfUhAIgmWg5WH",  # This key is expired and only here for demo reasons
)
