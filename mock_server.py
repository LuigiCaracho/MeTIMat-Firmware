from datetime import datetime
from typing import List

import uvicorn
from config import API_LISTEN_HOST, API_PORT, API_URL
from fastapi import FastAPI
from pydantic import BaseModel

# Import schemas
# Assuming running from machine-firmware directory
from schemas.order import Order
from schemas.prescription import Prescription

app = FastAPI()


class ScanRequest(BaseModel):
    qr_data: str


@app.post("/api/scan", response_model=Order)
async def scan(request: ScanRequest):
    print(f"📥 POST erhalten: {request.qr_data}")

    # Mock response using Order model
    # We create a dummy order
    response = Order(
        id=1,
        user_id=1,
        status="pending",
        created_at=datetime.now(),
        updated_at=datetime.now(),
        prescriptions=[
            Prescription(
                id=101,
                order_id=1,
                medication_id=50,
                medication_name="Ibuprofen 400mg",
                pzn="12345678",
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )
        ],
    )
    return response


if __name__ == "__main__":
    print(f"API Server läuft auf {API_URL}")
    uvicorn.run(app, host=API_LISTEN_HOST, port=API_PORT)
