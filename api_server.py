from flask import Flask, jsonify, request

app = Flask(__name__)


@app.route("/api/scan", methods=["POST"])
def scan():
    data = request.json
    print(f"📥 POST erhalten: {data}")
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    print("🟢 API Server läuft auf http://127.0.0.1:5000")
    app.run(port=5000)
