
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from PIL import Image
import io
import base64
from diamondpaintinggenerator import generate_diamond_painting
from paintbynumbersgenerator import generate_paint_by_numbers

app = Flask(__name__)
CORS(app)

@app.route("/process-diamond", methods=["POST"])
def process_diamond():
    if "image" not in request.files:
        return jsonify({"error": "Geen afbeelding"}), 400
    try:
        file = request.files["image"]
        image = Image.open(file.stream).convert("RGB")
        shape = request.form.get("shape", "square")
        preview_img, canvas_info = generate_diamond_painting(image, shape)

        preview_io = io.BytesIO()
        preview_img.save(preview_io, format="PNG")
        preview_io.seek(0)
        return send_file(preview_io, mimetype="image/png", as_attachment=False,
                         download_name="diamond_preview.png")
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/process-numbers", methods=["POST"])
def process_numbers():
    if "image" not in request.files:
        return jsonify({"error": "Geen afbeelding"}), 400
    try:
        file = request.files["image"]
        image = Image.open(file.stream).convert("RGB")
        num_colors = int(request.form.get("colors", 24))
        result = generate_paint_by_numbers(image, num_colors)

        # preview (verkleind)
        preview = result.copy()
        preview.thumbnail((400, 400))
        preview_io = io.BytesIO()
        preview.save(preview_io, format="PNG")
        preview_b64 = base64.b64encode(preview_io.getvalue()).decode("utf-8")

        return jsonify({ "preview": f"data:image/png;base64,{preview_b64}" })
    except Exception as e:
        return jsonify({"error": f"Fout tijdens verwerking: {str(e)}"}), 500

@app.route("/")
def home():
    return "✅ HappyHobby API draait correct"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
