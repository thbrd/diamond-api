
import base64
import uuid
import os
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from PIL import Image
from paintbynumbersgenerator import generate_paint_by_numbers
import io

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

        canvas_img = generate_paint_by_numbers(image, num_colors)

        unique_id = str(uuid.uuid4())
        canvas_filename = f"canvas_{unique_id}.png"
        canvas_path = os.path.join(STATIC_DIR, canvas_filename)
        canvas_img.save(canvas_path)

        base_url = "http://91.98.21.195:5000"
        return jsonify({
            "preview": f"{base_url}/static/{canvas_filename}"
        })
    except Exception as e:
        return jsonify({"error": f"Fout tijdens verwerking: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
