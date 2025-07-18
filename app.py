
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


    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Processing error: {str(e)}"}), 500
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Processing error: {str(e)}"}), 500

@app.route("/legend", methods=["POST"])
def legend():
    try:
        if not os.path.exists("used_codes.json"):
            return jsonify({"error": "No codes available"}), 400
        with open("used_codes.json") as f:
            codes = json.load(f)

        if not codes or not isinstance(codes, list):
            return jsonify({"error": "Code list is empty or invalid"}), 400

        used = [DMC_COLORS[c] for c in codes if c < len(DMC_COLORS)]
        height = len(used) * 30
        legend = Image.new("RGB", (300, height), (255, 255, 255))
        draw = ImageDraw.Draw(legend)

        for i, color in enumerate(used):
            draw.rectangle([10, i*30+5, 40, i*30+25], fill=tuple(color["rgb"]), outline="black")
            draw.text((50, i*30+8), f"DMC {color['code']} - {color['name']}", fill=(0,0,0))

        output = io.BytesIO()
        legend.save(output, format="PNG")
        output.seek(0)
        return send_file(output, mimetype="image/png")
    except Exception as e:
        return jsonify({"error": f"Legend generation failed: {str(e)}"}), 500

@app.route("/")
def home():
    return "✅ Diamond Painting API is live"


@app.route("/process_preview", methods=["POST"])
def process_preview():
    if "image" not in request.files:
        return jsonify({"error": "No image provided"}), 400
    try:
        file = request.files["image"]
        image = Image.open(file.stream).convert("RGB")

        # Genereer full size canvas (zoals bij /process_full)
        (canvas_w, canvas_h), (stones_w, stones_h) = suggest_best_canvas_format(image)
        resized = image.resize((stones_w, stones_h), Image.Resampling.BICUBIC)
        canvas = Image.new("RGB", (stones_w * 10, stones_h * 10), (255, 255, 255))
        draw = ImageDraw.Draw(canvas)
        for y in range(stones_h):
            for x in range(stones_w):
                color = resized.getpixel((x, y))
                rect = [x * 10, y * 10, (x + 1) * 10, (y + 1) * 10]
                draw.rectangle(rect, fill=color, outline=(200, 200, 200))

        # Maak preview (breedte max 800px)
        preview = canvas.copy()
        max_width = 800
        w_percent = (max_width / float(preview.size[0]))
        h_size = int((float(preview.size[1]) * float(w_percent)))
        preview = preview.resize((max_width, h_size), Image.Resampling.LANCZOS)

        io_preview = io.BytesIO()
        preview.save(io_preview, format="PNG")
        io_preview.seek(0)
        return send_file(io_preview, mimetype="image/png")
    except Exception as e:
        return jsonify({"error": f"Preview processing error: {str(e)}"}), 500

@app.route("/process_full", methods=["POST"])
def process_full():
    if "image" not in request.files:
        return jsonify({"error": "No image provided"}), 400
    try:
        file = request.files["image"]
        image = Image.open(file.stream).convert("RGB")

        # Genereer full size canvas
        (canvas_w, canvas_h), (stones_w, stones_h) = suggest_best_canvas_format(image)
        resized = image.resize((stones_w, stones_h), Image.Resampling.BICUBIC)
        canvas = Image.new("RGB", (stones_w * 10, stones_h * 10), (255, 255, 255))
        draw = ImageDraw.Draw(canvas)
        for y in range(stones_h):
            for x in range(stones_w):
                color = resized.getpixel((x, y))
                rect = [x * 10, y * 10, (x + 1) * 10, (y + 1) * 10]
                draw.rectangle(rect, fill=color, outline=(200, 200, 200))

        result_io = io.BytesIO()
        canvas.save(result_io, format="PNG")
        result_io.seek(0)
        return send_file(result_io, mimetype="image/png", as_attachment=True, download_name="volledige_afbeelding.png")
    except Exception as e:
        return jsonify({"error": f"Full image processing error: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
