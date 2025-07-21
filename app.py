
from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
from PIL import Image, ImageDraw
import os
import uuid
import subprocess
import io
import json
import numpy as np
from diamondpaintinggenerator import map_to_dmc, suggest_best_canvas_format

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "/tmp"
OUTPUT_FOLDER = "static"
REPO_SCRIPT = "/opt/paintbynumbersgenerator/paintbynumbersgenerator.py"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# ✅ Paint by Numbers via CLI
@app.route("/process-numbers", methods=["POST"])
def process_numbers():
    if "image" not in request.files:
        return jsonify({"error": "Geen afbeelding geüpload."}), 400

    try:
        file = request.files["image"]
        colors = request.form.get("colors", "24")

        uid = str(uuid.uuid4())
        input_filename = f"{uid}.jpg"
        input_path = os.path.join(UPLOAD_FOLDER, input_filename)
        file.save(input_path)

        subprocess.run([
            "python3",
            REPO_SCRIPT,
            input_path,
            colors
        ], check=True)

        output_prefix = os.path.splitext(os.path.basename(input_path))[0]
        png_filename = f"{output_prefix}.png"
        svg_filename = f"{output_prefix}.svg"

        os.rename(f"{output_prefix}.png", os.path.join(OUTPUT_FOLDER, png_filename))
        os.rename(f"{output_prefix}.svg", os.path.join(OUTPUT_FOLDER, svg_filename))

        return jsonify({
            "png": f"/static/{png_filename}",
            "svg": f"/static/{svg_filename}"
        })

    except subprocess.CalledProcessError:
        return jsonify({"error": "Fout tijdens verwerking via CLI"}), 500


# ✅ Diamond Painting route - ongewijzigd
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

@app.route("/static/<path:filename>")
def serve_static(filename):
    return send_from_directory(OUTPUT_FOLDER, filename)

@app.route("/")
def home():
    return "✅ HappyHobby API actief (Diamond + Paint by Numbers CLI)"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
