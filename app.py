
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

def auto_suggest_format(image, max_canvas_cm=80, min_dpi=3.5):
    # typical DPI for detailed diamond painting: 3.5 to 5 dots per mm (~90-130 DPI)
    aspect_ratio = image.width / image.height

    max_width_stones = int((max_canvas_cm * 10) * min_dpi)  # 80cm × 10 × 3.5 = 2800 stones max
    width = min(max_width_stones, image.width)  # limit by original size if smaller
    height = int(width / aspect_ratio)
    return width, height

def map_to_dmc(image, width, height, stone_size=10):
    small = image.resize((width, height), Image.Resampling.BICUBIC)
    pixels = np.array(small).reshape(-1, 3)
    dists = np.linalg.norm(pixels[:, None] - DMC_RGB[None], axis=2)
    nearest = np.argmin(dists, axis=1)
    mapped = DMC_RGB[nearest].astype(np.uint8).reshape(height, width, 3)
    used_codes = sorted(set(nearest.tolist()))

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
        width, height = auto_suggest_format(image)
        result, codes, w, h = map_to_dmc(image, width, height)
        with open("used_codes.json", "w") as f:
            json.dump(codes, f)
        result_io = io.BytesIO()
        result.save(result_io, format="PNG")
        result_io.seek(0)
        response = send_file(result_io, mimetype="image/png")
        response.headers["X-Suggested-Stones-Width"] = str(w)
        response.headers["X-Suggested-Stones-Height"] = str(h)
        response.headers["X-Recommended-Canvas-CM"] = f"{int(w/3.5)} x {int(h/3.5)} cm"
        return response
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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
