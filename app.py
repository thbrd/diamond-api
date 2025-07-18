
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from sklearn.cluster import KMeans
import io

app = Flask(__name__)
CORS(app)  # ✅ Sta alle domeinen toe (of beperk naar jouw frontend domein)

@app.route("/")
def index():
    return "Diamond Painting API is live"

@app.route("/process", methods=["POST"])
def process():
    if 'image' not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    file = request.files['image']
    shape = request.form.get('shape', 'square')
    img = Image.open(file).convert("RGB")

    resize_width = 100
    aspect_ratio = img.height / img.width
    resize_height = int(resize_width * aspect_ratio)
    img_small = img.resize((resize_width, resize_height), resample=Image.BILINEAR)

    pixels = np.array(img_small).reshape(-1, 3)
    k = 20
    kmeans = KMeans(n_clusters=k, random_state=42).fit(pixels)
    palette = np.round(kmeans.cluster_centers_).astype(int)
    labels = kmeans.labels_

    steentje_grootte = 20
    preview = Image.new("RGB", (resize_width * steentje_grootte, resize_height * steentje_grootte), "white")
    draw = ImageDraw.Draw(preview)

    for y in range(resize_height):
        for x in range(resize_width):
            idx = y * resize_width + x
            color = tuple(palette[labels[idx]])
            cx = x * steentje_grootte
            cy = y * steentje_grootte
            if shape == 'round':
                draw.ellipse([cx, cy, cx + steentje_grootte, cy + steentje_grootte], fill=color, outline="gray")
            else:
                draw.rectangle([cx, cy, cx + steentje_grootte, cy + steentje_grootte], fill=color, outline="gray")

    preview_bytes = io.BytesIO()
    preview.save(preview_bytes, format='PNG')
    preview_bytes.seek(0)

    return send_file(preview_bytes, mimetype='image/png')

@app.route("/legend", methods=["POST"])
def download_legend():
    legend = Image.new("RGB", (300, 640), "white")
    d = ImageDraw.Draw(legend)
    font = ImageFont.load_default()
    for i in range(20):
        y = i * 30 + 10
        d.rectangle([10, y, 40, y + 20], fill=(100+i*7, 100+i*3, 150+i*2), outline="black")
        d.text((50, y + 4), f"Kleur {i+1}", fill="black", font=font)

    legend_bytes = io.BytesIO()
    legend.save(legend_bytes, format='PNG')
    legend_bytes.seek(0)

    return send_file(legend_bytes, mimetype='image/png')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
