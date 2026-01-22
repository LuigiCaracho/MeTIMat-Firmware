from flask import Flask, jsonify, request
from flask.typing import ResponseClass

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
    print("🟢 API Server läuft auf http://127.0.0.1:5000")
    app.run(port=5000)
