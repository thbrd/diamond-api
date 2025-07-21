
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import uuid
import subprocess

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "/tmp"
OUTPUT_FOLDER = "static"
REPO_SCRIPT = "/opt/paintbynumbersgenerator/paintbynumbersgenerator.py"  # <- pas dit pad aan op je VPS

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

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

        # Roep de CLI tool aan
        subprocess.run([
            "python3",
            REPO_SCRIPT,
            input_path,
            colors
        ], check=True)

        output_prefix = os.path.splitext(os.path.basename(input_path))[0]
        png_filename = f"{output_prefix}.png"
        svg_filename = f"{output_prefix}.svg"

        # Verplaats output naar static folder
        os.rename(f"{output_prefix}.png", os.path.join(OUTPUT_FOLDER, png_filename))
        os.rename(f"{output_prefix}.svg", os.path.join(OUTPUT_FOLDER, svg_filename))

        return jsonify({
            "png": f"/static/{png_filename}",
            "svg": f"/static/{svg_filename}"
        })

    except subprocess.CalledProcessError as e:
        return jsonify({"error": "Fout tijdens verwerking via CLI"}), 500

@app.route("/static/<path:filename>")
def serve_static(filename):
    return send_from_directory(OUTPUT_FOLDER, filename)

@app.route("/")
def home():
    return "✅ Paint by Numbers CLI server actief"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
