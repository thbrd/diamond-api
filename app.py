
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
os.makedirs(STATIC_DIR, exist_ok=True)

app = Flask(__name__, static_folder="static")
app.secret_key = "supersecretkey"
CORS(app)

@app.route("/process-numbers", methods=["POST"])
def process_numbers():
    if "image" not in request.files:
        return jsonify({"error": "No image provided"}), 400
    try:
        file = request.files["image"]
        image = Image.open(file.stream).convert("RGB")
        num_colors = int(request.form.get("colors", 24))

        log_request("paintbynumbers")
        result_image = generate_paint_by_numbers(image, num_colors)

        unique_id = str(uuid.uuid4())
        result_path = os.path.join(STATIC_DIR, f"{unique_id}_pbn.png")
        result_image.save(result_path)

        return jsonify({
            "preview": f"http://91.98.21.195:5000/static/{unique_id}_pbn.png"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
