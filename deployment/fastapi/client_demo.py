import requests

if __name__ == "__main__":
    url = "http://127.0.0.1:8000/predict"
    # Replace feature values below with real feature vectors expected by your model
    payload = {
        "instances": [
            [0.0, 1.2, 3.4],
            [4.5, 6.7, 8.9]
        ]
    }
    try:
        r = requests.post(url, json=payload, timeout=10)
        print("Status:", r.status_code)
        print("Response:", r.json())
    except Exception as e:
        print("Request failed:", e)
