from pathlib import Path
from typing import Any, Optional, List

from fastapi import FastAPI, HTTPException, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse

# Optional joblib import; fall back to pickle
try:
    import joblib  # type: ignore
except Exception:
    joblib = None  # type: ignore
import pickle


app = FastAPI(title="Simple Weather Model Demo", version="1.0.0")

# Resolve model path relative to repository root
ROOT_DIR = Path(__file__).resolve().parents[2]
MODEL_RELATIVE = Path("models") / "random-forest-model.pkl"
MODEL_PATH = ROOT_DIR / MODEL_RELATIVE
LABEL_ENCODER_RELATIVE = Path("models") / "label-encoder.pkl"
LABEL_ENCODER_PATH = ROOT_DIR / LABEL_ENCODER_RELATIVE

model: Optional[Any] = None
model_load_error: Optional[str] = None
label_encoder: Optional[Any] = None
label_encoder_error: Optional[str] = None

FEATURE_ORDER = ["precipitation", "temp_max", "temp_min", "wind"]


def load_model() -> Optional[Any]:
    """Attempt to load the model from disk; set global state."""
    global model, model_load_error
    if not MODEL_PATH.exists():
        model_load_error = f"Model file not found at: {MODEL_PATH}"
        model = None
        return None
    try:
        if joblib is not None:
            model = joblib.load(MODEL_PATH)  # type: ignore[attr-defined]
        else:
            with open(MODEL_PATH, "rb") as f:
                model = pickle.load(f)
        model_load_error = None
        return model
    except Exception as e:
        model = None
        model_load_error = f"Failed to load model: {e}"
        return None


@app.on_event("startup")
def _startup() -> None:
    load_model()
    load_label_encoder()


def load_label_encoder() -> Optional[Any]:
    """Optionally load a LabelEncoder to map numeric predictions to names."""
    global label_encoder, label_encoder_error
    if not LABEL_ENCODER_PATH.exists():
        label_encoder = None
        label_encoder_error = "Label encoder file not found"
        return None
    try:
        if joblib is not None:
            label_encoder = joblib.load(LABEL_ENCODER_PATH)  # type: ignore[attr-defined]
        else:
            with open(LABEL_ENCODER_PATH, "rb") as f:
                label_encoder = pickle.load(f)
        label_encoder_error = None
        return label_encoder
    except Exception as e:
        label_encoder = None
        label_encoder_error = f"Failed to load label encoder: {e}"
        return None


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok" if model is not None else "degraded",
        "model_path": str(MODEL_RELATIVE),
        "model_exists": MODEL_PATH.exists(),
        "model_loaded": model is not None,
        "label_encoder_path": str(LABEL_ENCODER_RELATIVE),
        "label_encoder_exists": LABEL_ENCODER_PATH.exists(),
        "label_encoder_loaded": label_encoder is not None,
        "error": model_load_error,
        "label_encoder_error": label_encoder_error,
    }


def render_form(prediction: Optional[Any] = None, error: Optional[str] = None) -> str:
    msg = "" if prediction is None and not error else (
        f"<div class='msg ok'>Prediction: <b>{prediction}</b></div>" if error is None else f"<div class='msg err'>Error: {error}</div>"
    )
    return f"""
<!doctype html>
<html lang='en'>
  <head>
    <meta charset='utf-8'>
    <meta name='viewport' content='width=device-width, initial-scale=1'>
    <title>Simple Weather Model Demo</title>
    <style>
      body{{font-family:system-ui,-apple-system,Segoe UI,Roboto,Ubuntu,sans-serif;margin:0;background:#0b1020;color:#eef}}
      .wrap{{max-width:720px;margin:24px auto;padding:0 16px}}
      h1{{font-size:20px;margin:0 0 12px}}
      .card{{background:#12193a;border:1px solid #2a325a;border-radius:8px;padding:16px;margin-bottom:16px}}
      label{{display:block;margin:8px 0 4px}}
      input[type=number]{{width:100%;padding:8px;border-radius:6px;border:1px solid #2a325a;background:#0b1020;color:#eef}}
      button{{margin-top:12px;background:#4050ff;border:none;color:#fff;padding:10px 14px;border-radius:6px;cursor:pointer}}
      button:hover{{background:#3040e0}}
      .msg{{margin-top:12px;padding:10px;border-radius:6px}}
      .ok{{background:#113b11;border:1px solid #1f6e1f}}
      .err{{background:#3b1111;border:1px solid #6e1f1f}}
      small{{color:#9ac}}
      .grid{{display:grid;gap:12px;grid-template-columns:1fr 1fr}}
      @media (max-width:640px){{.grid{{grid-template-columns:1fr}}}}
    </style>
  </head>
  <body>
    <div class='wrap'>
      <div class='card'>
        <h1>Weather Prediction (Form)</h1>
        <form method='post' action='/'>
          <div class='grid'>
            <div>
              <label>precipitation</label>
              <input name='precipitation' type='number' step='any' required>
            </div>
            <div>
              <label>temp_max</label>
              <input name='temp_max' type='number' step='any' required>
            </div>
            <div>
              <label>temp_min</label>
              <input name='temp_min' type='number' step='any' required>
            </div>
            <div>
              <label>wind</label>
              <input name='wind' type='number' step='any' required>
            </div>
          </div>
          <button type='submit'>Predict</button>
        </form>
        {msg}
        <small>Atau kirim JSON ke POST /predict dengan body: {{"records":[{{"precipitation":0,"temp_max":1,"temp_min":0,"wind":2}}]}}</small>
      </div>
      <div class='card'>
        <h2>Health</h2>
        <small>Model path: {MODEL_RELATIVE}</small>
      </div>
    </div>
  </body>
 </html>
    """


@app.get("/", response_class=HTMLResponse)
def root_get():
    return HTMLResponse(render_form())


@app.post("/", response_class=HTMLResponse)
def root_post(
    precipitation: float = Form(...),
    temp_max: float = Form(...),
    temp_min: float = Form(...),
    wind: float = Form(...),
):
    if model is None:
        load_model()
    if model is None:
        return HTMLResponse(render_form(error=model_load_error or "Model not loaded"))
    try:
        X = [[precipitation, temp_max, temp_min, wind]]
        y_pred = model.predict(X)  # type: ignore[operator]
        # Convert to Python types
        try:
            encoded_list = y_pred.tolist()
        except Exception:
            encoded_list = list(y_pred)

        # If already string labels, use directly; else map via label encoder if available
        first = encoded_list[0]
        if isinstance(first, str):
            label = first
        elif label_encoder is not None:
            try:
                label = label_encoder.inverse_transform([first])[0]
            except Exception:
                label = first
        else:
            label = first

        return HTMLResponse(render_form(prediction=label))
    except Exception as e:
        return HTMLResponse(render_form(error=f"Prediction failed: {e}"))


@app.post("/predict")
async def predict(request: Request):
    # Lazy reload if needed (useful for some hot-reload flows)
    if model is None:
        load_model()
    if model is None:
        raise HTTPException(status_code=500, detail=model_load_error or "Model not loaded")
    try:
        data = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body")
    records = data.get("records")
    if not isinstance(records, list) or not records:
        raise HTTPException(status_code=400, detail="Body must include 'records': [ {precipitation,temp_max,temp_min,wind} ]")
    try:
        X: List[List[float]] = [
            [
                float(r["precipitation"]),
                float(r["temp_max"]),
                float(r["temp_min"]),
                float(r["wind"]),
            ]
            for r in records
        ]
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid record values: {e}")

    try:
        y_pred = model.predict(X)  # type: ignore[operator]
        try:
            encoded = y_pred.tolist()
        except AttributeError:
            encoded = list(y_pred)

        # If already string labels, return directly; else try inverse transform
        if len(encoded) > 0 and isinstance(encoded[0], str):
            labels = encoded
        elif label_encoder is not None:
            try:
                labels = label_encoder.inverse_transform(encoded)
                if hasattr(labels, "tolist"):
                    labels = labels.tolist()
                else:
                    labels = list(labels)
            except Exception:
                labels = encoded
        else:
            labels = encoded

        return JSONResponse({"predictions": labels})
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Prediction failed: {e}")

