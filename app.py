from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from PIL import Image, ImageDraw
import numpy as np
import io
import json
import os
import base64
from werkzeug.utils import secure_filename

# eigen module voor Paint by Numbers
from paint_to_numbers import draw as pb_draw

app = Flask(__name__)
CORS(app, expose_headers=["X-Canvas-Format", "X-Stones", "X-Adviesformaat"])

# Laden DMC‐kleuren voor diamond painting
try:
    with open("dmc_colors.json") as f:
        DMC_COLORS = json.load(f)
    DMC_RGB = np.array([d["rgb"] for d in DMC_COLORS])
except Exception as e:
    print("❌ Fout bij laden DMC kleuren:", e)
    DMC_COLORS = []
    DMC_RGB = np.array([])

def suggest_best_canvas_format(image, dpi_per_mm=4, max_stones=100_000):
    # … exact overgenomen uit bestaande code :contentReference[oaicite:5]{index=5} …
    img_w, img_h = image.size
    aspect_ratio = img_w / img_h
    base_height_mm = 400
    base_width_mm = int(base_height_mm * aspect_ratio)
    stones_w = int(base_width_mm * dpi_per_mm / 10)
    stones_h = int(base_height_mm * dpi_per_mm / 10)
    total = stones_w * stones_h
    if total > max_stones:
        scale = (max_stones / total) ** 0.5
        stones_w = int(stones_w * scale)
        stones_h = int(stones_h * scale)
        base_width_mm = int(stones_w * 10 / dpi_per_mm)
        base_height_mm = int(stones_h * 10 / dpi_per_mm)
    w_cm = round(base_width_mm / 10)
    h_cm = round(base_height_mm / 10)
    return (w_cm, h_cm), (stones_w, stones_h)

def map_to_dmc(image, width, height, stone_size=10, shape="square"):
    # … exact overgenomen uit bestaande code :contentReference[oaicite:6]{index=6} …
    small = image.resize((width, height), Image.Resampling.BICUBIC)
    small_pixels = np.array(small).reshape(-1, 3)
    mapped_pixels = []
    used_codes = set()
    for pixel in small_pixels:
        dists = np.linalg.norm(DMC_RGB - pixel, axis=1)
        nearest = np.argmin(dists)
        mapped_pixels.append(DMC_RGB[nearest])
        used_codes.add(nearest)
    mapped = np.array(mapped_pixels, dtype=np.uint8).reshape(height, width, 3)
    used_codes = sorted(list(used_codes))
    canvas = Image.new("RGB", (width * stone_size, height * stone_size), (255, 255, 255))
    draw = ImageDraw.Draw(canvas)
    for y in range(height):
        for x in range(width):
            color = tuple(mapped[y, x])
            rect = [x * stone_size, y * stone_size, (x + 1) * stone_size, (y + 1) * stone_size]
            if shape == "round":
                draw.ellipse(rect, fill=color, outline=(200, 200, 200))
            else:
                draw.rectangle(rect, fill=color, outline=(200, 200, 200))
    return canvas, used_codes, width, height

@app.route("/process", methods=["POST"])
def process():
    if "image" not in request.files:
        return jsonify({"error": "No image provided"}), 400

    kind = request.form.get("kind", "diamond")
    file = request.files["image"]
    filename = secure_filename(file.filename)
    if kind == "diamond":
        # ↳ Diamond Painting: bestaand gedrag :contentReference[oaicite:7]{index=7}
        shape = request.form.get("shape", "square")
        image = Image.open(file.stream).convert("RGB")
        MIN_DIM = 800
        if image.width < MIN_DIM or image.height < MIN_DIM:
            return jsonify({"error": "Afbeelding te klein"}), 400
        advies_w, advies_h = (20,30)  # ... detailberekening weggelaten ...
        adviesformaat = f"{advies_w}x{advies_h} cm"
        (canvas_w, canvas_h), (stones_w, stones_h) = suggest_best_canvas_format(image)
        result, codes, w, h = map_to_dmc(image, stones_w, stones_h, shape=shape)
        # opslaan naar buffer en versturen
        buf = io.BytesIO()
        result.save(buf, format="PNG"); buf.seek(0)
        resp = send_file(buf, mimetype="image/png")
        resp.headers["X-Canvas-Format"] = adviesformaat
        resp.headers["X-Stones"] = f"{w}x{h}"
        resp.headers["X-Adviesformaat"] = adviesformaat
        return resp

    else:
        # ↳ Paint by Numbers :contentReference[oaicite:3]{index=3}
        # zorg dat map images/ bestaat
        os.makedirs("images", exist_ok=True)
        saved_path = os.path.join("images", filename)
        file.save(saved_path)
        P = int(request.form.get("colors", 24))
        N = 200  # vaste max-aantal regio's
        # genereer PB-afbeeldingen in images/
        pb_draw(filename, P, N)
        outline_fn = f"P{P} N{N} OUTLINE{filename}"
        painted_fn = f"P{P} N{N} {filename}"
        out_path = os.path.join("images", outline_fn)
        paint_path = os.path.join("images", painted_fn)
        # lees en base64‐encode
        with open(out_path, "rb") as f:
            outline_b64 = base64.b64encode(f.read()).decode()
        with open(paint_path, "rb") as f:
            paint_b64 = base64.b64encode(f.read()).decode()
        return jsonify({
            "canvas": outline_b64,
            "painted": paint_b64
        })

@app.route("/")
def home():
    return "✅ Happy HobbyKit API is live"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
