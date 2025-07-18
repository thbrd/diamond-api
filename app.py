
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from PIL import Image, ImageDraw
import numpy as np
import io
import json
import os

app = Flask(__name__)
CORS(app)

try:
    with open("dmc_colors.json") as f:
        DMC_COLORS = json.load(f)
    DMC_RGB = np.array([d["rgb"] for d in DMC_COLORS])
except Exception as e:
    print("❌ Fout bij laden DMC kleuren:", e)
    DMC_COLORS = []
    DMC_RGB = np.array([])

def suggest_best_canvas_format(image, dpi_per_mm=4, max_stones=100_000):
    formats = [(30,40), (40,50), (50,70), (60,80)]
    img_ratio = image.width / image.height

    def format_diff(fmt):
        w, h = fmt
        return abs((w/h) - img_ratio)

    best_format = min(formats, key=format_diff)
    w_cm, h_cm = best_format

    stones_w = int(w_cm * 10 * dpi_per_mm)
    stones_h = int(h_cm * 10 * dpi_per_mm)

    total = stones_w * stones_h
    if total > max_stones:
        scale = (max_stones / total) ** 0.5
        stones_w = int(stones_w * scale)
        stones_h = int(stones_h * scale)
        w_cm = round(stones_w / (10 * dpi_per_mm))
        h_cm = round(stones_h / (10 * dpi_per_mm))

    return (w_cm, h_cm), (stones_w, stones_h)

def map_to_dmc(image, width, height, stone_size=10):
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
            draw.rectangle(rect, fill=color, outline=(200, 200, 200))

    return canvas, used_codes, width, height


@app.route("/process", methods=["POST"])
def process():
    if "image" not in request.files:
        return jsonify({"error": "No image provided"}), 400
    try:
        file = request.files["image"]
        image = Image.open(file.stream).convert("RGB")

        # Gebruik originele afmetingen
        width, height = image.size

        # Mappen naar DMC met originele afmeting
        full_canvas, codes, _, _ = map_to_dmc(image, width, height)
        codes = [int(c) for c in codes]
        with open("used_codes.json", "w") as f:
            json.dump(codes, f)

        # Preview maken (geschaald, bijvoorbeeld breedte 300px behoud aspect ratio)
        preview_width = 300
        ratio = preview_width / full_canvas.width
        preview_height = int(full_canvas.height * ratio)
        preview = full_canvas.resize((preview_width, preview_height), Image.Resampling.LANCZOS)

        # Beide versies in geheugen
        full_io = io.BytesIO()
        preview_io = io.BytesIO()
        full_canvas.save(full_io, format="PNG")
        preview.save(preview_io, format="PNG")
        full_io.seek(0)
        preview_io.seek(0)

        # Voeg beide bestanden toe aan multipart response
        from flask import send_file, make_response
        import zipfile

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("diamond_painting.png", full_io.read())
            zf.writestr("preview.png", preview_io.read())
        zip_buffer.seek(0)

        response = send_file(zip_buffer, mimetype="application/zip", as_attachment=True, download_name="diamond_result.zip")
        response.headers["X-Stones"] = f"{width} x {height}"
        return response
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Processing error: {str(e)}"}), 500

    except Exception as e:
        return jsonify({"error": f"Legend generation failed: {str(e)}"}), 500

@app.route("/")
def home():
    return "✅ Diamond Painting API is live"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
