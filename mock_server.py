from datetime import datetime
from typing import Any, Dict, List, Optional

import uvicorn
from config import API_LISTEN_HOST, API_LISTEN_PORT, API_URL, MACHINE_ACCESS_TOKEN
from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel
from schemas.location import Location

# Import schemas
# Assuming running from machine-firmware directory
from schemas.order import Order
from schemas.prescription import Prescription

app = FastAPI()


class ScanRequest(BaseModel):
    qr_data: str


class ValidationResponse(BaseModel):
    valid: bool
    order: Optional[Order] = None
    message: str
    location_id: Optional[int] = None


@app.post("/api/v1/orders/validate-qr", response_model=ValidationResponse)
async def validate_qr(
    request: ScanRequest,
    x_machine_token: Optional[str] = Header(None, alias="X-Machine-Token"),
):
    """
    Validates a QR code using the machine access token and returns order details.
    """
    print(f"📥 QR-Validation erhalten: {request.qr_data}")
    print(f"🔑 Machine Token: {x_machine_token}")

    # Check machine authorization
    if x_machine_token != MACHINE_ACCESS_TOKEN:
        print("❌ Ungültiger Machine Token")
        return ValidationResponse(valid=False, message="Machine authorization failed")

    # Mock logic: Accept any non-empty QR data as valid for the mock
    if not request.qr_data or len(request.qr_data) < 3:
        return ValidationResponse(valid=False, message="Invalid QR data")

    # Create mock order details
    mock_order = Order(
        id=7,
        user_id=1,
        status="available for pickup",
        created_at=datetime.now(),
        updated_at=datetime.now(),
        prescriptions=[
            Prescription(
                id=101,
                order_id=7,
                medication_id=50,
                medication_name="Ibuprofen 400mg Lysinat",
                pzn="04126127",
                created_at=datetime.now(),
                updated_at=datetime.now(),
            ),
            Prescription(
                id=102,
                order_id=7,
                medication_id=62,
                medication_name="Naspray AL 0,1%",
                pzn="03417124",
                created_at=datetime.now(),
                updated_at=datetime.now(),
            ),
        ],
        location=Location(
            id=42,
            name="MeTIMat Automat - Campus Nord",
            address="Kaiserstraße 12, 76131 Karlsruhe",
            latitude=49.00937,
            longitude=8.41165,
            is_available=True,
        ),
    )

    # Note: The Order schema in schemas/order.py might not have locationReference,
    # but the frontend expects it. We can handle this by returning a dict or extending.

    return ValidationResponse(
        valid=True,
        order=mock_order,
        message="QR-Code erfolgreich validiert",
        location_id=42,
    )


# Legacy endpoint for compatibility during transition
@app.post("/api/scan")
async def legacy_scan(request: ScanRequest):
    return await validate_qr(request, MACHINE_ACCESS_TOKEN)


if __name__ == "__main__":
    print(f"API Server läuft auf http://{API_LISTEN_HOST}:{API_LISTEN_PORT}")
    uvicorn.run(app, host=API_LISTEN_HOST, port=API_LISTEN_PORT)
