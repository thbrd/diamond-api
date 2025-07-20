from paintbynumbersgenerator import generate_paint_by_numbers
from flask import send_file, Flask, request, jsonify, send_file
from flask_cors import CORS
from PIL import Image, ImageDraw
import numpy as np
import io
import json
import os
import base64

app = Flask(__name__)
CORS(app, expose_headers=["X-Canvas-Format", "X-Stones", "X-Adviesformaat"])

try:
    with open("dmc_colors.json") as f:
        DMC_COLORS = json.load(f)
    DMC_RGB = np.array([d["rgb"] for d in DMC_COLORS])
except Exception as e:
    print("❌ Fout bij laden DMC kleuren:", e)
    DMC_COLORS = []
    DMC_RGB = np.array([])


def suggest_best_canvas_format(image, dpi_per_mm=4, max_stones=100_000):
    img_w, img_h = image.size
    aspect_ratio = img_w / img_h

    # Stel standaard canvas hoogte in mm
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
    try:
        file = request.files["image"]
        image = Image.open(file.stream).convert("RGB")
        shape = request.form.get("shape", "square")

        # Afmeting controleren
        MIN_WIDTH = 800
        MIN_HEIGHT = 800
        if image.width < MIN_WIDTH or image.height < MIN_HEIGHT:
            return jsonify({"error": "De foto is te klein voor een scherp eindresultaat. Upload een grotere afbeelding."}), 400

        # Bekende diamond painting formaten
        standaard_formaten = [
            (20, 30), (30, 40), (40, 50), (50, 60),
            (60, 80), (80, 100), (90, 120), (100, 150)
        ]

        # Bepaal beeldverhouding
        aspect_ratio = image.width / image.height

        # Zoek formaat met dichtstbijzijnde verhouding
        def formaat_score(f):
            w, h = f
            return abs((w / h) - aspect_ratio)

        advies_w, advies_h = min(standaard_formaten, key=formaat_score)
        adviesformaat = f"{advies_w}x{advies_h} cm"
        show_warning = (advies_w, advies_h) == (20, 30) or (advies_w, advies_h) == (30, 20)

        (canvas_w, canvas_h), (stones_w, stones_h) = suggest_best_canvas_format(image)
        result, codes, w, h = map_to_dmc(image, stones_w, stones_h, shape=shape)
        codes = [int(c) for c in codes]
        with open("used_codes.json", "w") as f:
            json.dump(codes, f)
        result_io = io.BytesIO()
        result.save(result_io, format="PNG")
        result_io.seek(0)
        response = send_file(result_io, mimetype="image/png")
        response.headers["X-Canvas-Format"] = f"{canvas_w}x{canvas_h} cm"
        response.headers["X-Stones"] = f"{w} x {h}"
        response.headers["X-Adviesformaat"] = adviesformaat
        response.headers["X-Warning"] = "1" if show_warning else "0"
        return response

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Processing error: {str(e)}"}), 500

@app.route("/")
def home():
    return "✅ Diamond Painting API is live"

@app.route("/process-numbers", methods=["POST"])
def process_numbers():
    if "image" not in request.files:
        return jsonify({"error": "Geen afbeelding geüpload."}), 400
    try:
        file = request.files["image"]
        image = Image.open(file.stream).convert("RGB")
        num_colors = int(request.form.get("colors", 24))
        result = generate_paint_by_numbers(image, num_colors)

        # Verkleinde preview voor weergave
        preview = result.copy()
        preview.thumbnail((400, 400))
        preview_io = io.BytesIO()
        preview.save(preview_io, format="PNG")
        preview_io.seek(0)
        return send_file(preview_io, mimetype="image/png")
    except Exception as e:
        return jsonify({"error": f"Fout tijdens verwerking: {str(e)}"}), 500
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
