"""AgriVision backend (serves the website + prediction API).

Setup:  py -3.12 -m pip install flask tensorflow pillow numpy
Put server.py, index.html, style.css, script.js, plant_disease_model.keras and disease_info.json in ONE folder.
Run:    py -3.12 server.py     then open  http://localhost:5000  in Chrome or Edge.
"""
import json, os, threading
import numpy as np
import tensorflow as tf
from flask import Flask, jsonify, request, send_from_directory
from PIL import Image

D = os.path.dirname(os.path.abspath(__file__))
model = tf.keras.models.load_model(os.path.join(D, "plant_disease_model.keras"))
kb = json.load(open(os.path.join(D, "disease_info.json"), encoding="utf-8"))

CLASSES = ['Pepper__bell___Bacterial_spot', 'Pepper__bell___healthy', 'Potato___Early_blight',
           'Potato___Late_blight', 'Potato___healthy', 'Tomato_Bacterial_spot', 'Tomato_Early_blight',
           'Tomato_Late_blight', 'Tomato_Leaf_Mold', 'Tomato_Septoria_leaf_spot',
           'Tomato_Spider_mites_Two_spotted_spider_mite', 'Tomato__Target_Spot',
           'Tomato__Tomato_YellowLeaf__Curl_Virus', 'Tomato__Tomato_mosaic_virus', 'Tomato_healthy']
THRESHOLD = 0.70
FIELDS = ("disease_name", "crop", "symptoms", "cause", "general_management", "prevention")
lock = threading.Lock()

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 12 * 1024 * 1024


def looks_like_leaf(img, min_ratio=0.15):
    """Colour heuristic: share of green/yellow-brown pixels. Filters obvious non-leaf photos."""
    h = np.array(img.resize((100, 100)).convert("HSV")).astype(int)
    return ((h[..., 0] >= 20) & (h[..., 0] <= 100) & (h[..., 1] >= 30)).mean() >= min_ratio


@app.get("/")
def home():
    return send_from_directory(D, "index.html")


@app.get("/<name>")
def assets(name):
    if name in ("style.css", "script.js"):
        return send_from_directory(D, name)
    return "Not found", 404


@app.after_request
def allow_local_page(r):
    r.headers["Access-Control-Allow-Origin"] = "*"
    return r


@app.post("/api/predict")
def predict():
    f = request.files.get("image")
    if not f:
        return jsonify(status="error", message="No image received"), 400
    try:
        img = Image.open(f.stream).convert("RGB")
    except Exception:
        return jsonify(status="error", message="Could not read this image"), 400

    if not looks_like_leaf(img):
        return jsonify(status="not_leaf")

    x = np.expand_dims(np.array(img.resize((224, 224)), dtype="float32"), 0)
    x = tf.keras.applications.mobilenet_v2.preprocess_input(x)
    with lock:
        p = model.predict(x, verbose=0)[0]
    i = int(p.argmax())
    conf = float(p[i])

    if conf < THRESHOLD:
        return jsonify(status="uncertain", confidence=conf)
    info = kb.get(CLASSES[i], {})
    return jsonify(status="prediction", confidence=conf, **{k: info.get(k) for k in FIELDS})


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
