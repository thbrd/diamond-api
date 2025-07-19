
import base64
import uuid
import os
import io
from flask import Flask, request, jsonify, send_file, session, redirect
from flask_cors import CORS
from PIL import Image
from paintbynumbersgenerator import generate_paint_by_numbers
from diamondpaintinggenerator import generate_diamond_painting
from utils import log_request, get_logs, clear_generated_files

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
app = Flask(__name__, static_folder="static")
app.secret_key = "supersecretkey"
CORS(app)

@app.route("/process-numbers", methods=["POST"])
def process_numbers():
    if "image" not in request.files:
        return jsonify({ "error": "No image uploaded" }), 400

    image_file = request.files["image"]
    colors = int(request.form.get("colors", 8))

    image = Image.open(image_file.stream).convert("RGB")

    result_img = generate_paint_by_numbers(image, colors)

    filename = f"pbn_{uuid.uuid4().hex}.png"
    filepath = os.path.join(STATIC_DIR, filename)
    result_img.save(filepath)

    return jsonify({ "preview": f"/static/{filename}" })

@app.route("/clear", methods=["POST"])
def clear():
    clear_generated_files(STATIC_DIR)
    return "Cleared", 200

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
