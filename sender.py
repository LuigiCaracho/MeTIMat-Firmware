import requests


def send_scan(url, value):
    payload = {"scan": value}

    try:
        response = requests.post(url, json=payload, timeout=3)
        print(f"📤 POST {response.status_code}: {value}")
    except Exception as e:
        print(f"❌ POST fehlgeschlagen: {e}")
