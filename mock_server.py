from config import API_LISTEN_HOST, API_PORT, API_URL
from flask import Flask, jsonify, request

app = Flask(__name__)


@app.route("/api/scan", methods=["POST"])
def scan():
    data = request.json
    print(f"📥 POST erhalten: {data}")
    response = {
        "valid": True,
        "message": "QR-Code erfolgreich validiert",
        "profile": "Testprofil",
        "error": None,
    }
    return jsonify(response)


if __name__ == "__main__":
    print(f"API Server läuft auf {API_URL}")
    app.run(port=API_PORT, host=API_LISTEN_HOST)
