
from flask import Flask, request, send_file, jsonify, make_response
from flask_cors import CORS
from PIL import Image
import io
import os
import json
import numpy as np
from uuid import uuid4

from paintbynumbersgenerator import generate_paint_by_numbers_svg_png

app = Flask(__name__)
CORS(app, expose_headers=["X-Download-URL"])

@app.route("/process-numbers", methods=["POST"])
def process_numbers():
    if "image" not in request.files:
        return jsonify({"error": "Geen afbeelding geüpload."}), 400
    try:
        file = request.files["image"]
        image = Image.open(file.stream).convert("RGB")
        num_colors = int(request.form.get("colors", 24))

        svg_str, full_png = generate_paint_by_numbers_svg_png(image, num_colors)

        file_id = str(uuid4())
        png_filename = f"{file_id}.png"
        png_path = os.path.join("static", png_filename)
        full_png.save(png_path)

        response = make_response(svg_str)
        response.headers["Content-Type"] = "image/svg+xml"
        response.headers["X-Download-URL"] = f"/static/{png_filename}"
        return response
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/")
def home():
    return "✅ Paint by Numbers API live"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
