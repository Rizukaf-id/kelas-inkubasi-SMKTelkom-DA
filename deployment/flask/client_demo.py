import requests

if __name__ == "__main__":
    url = "http://127.0.0.1:8000/predict"
    payload = {
        "records": [
            {"precipitation": 0.0, "temp_max": 1.2, "temp_min": -0.5, "wind": 2.3},
            {"precipitation": 4.5, "temp_max": 6.7, "temp_min": 1.1, "wind": 0.9}
        ]
    }
    try:
        r = requests.post(url, json=payload, timeout=10)
        print("Status:", r.status_code)
        print("Response:", r.json())
    except Exception as e:
        print("Request failed:", e)
