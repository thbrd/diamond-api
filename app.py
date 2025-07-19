
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from PIL import Image
import io
import base64
from paintbynumbersgenerator import generate_paint_by_numbers

app = Flask(__name__)
CORS(app)

@app.route("/paint-by-numbers", methods=["POST"])
def handle_paint_by_numbers():
    if "image" not in request.files:
        return jsonify({"error": "Geen afbeelding geüpload."}), 400

    try:
        file = request.files["image"]
        image = Image.open(file.stream).convert("RGB")
        num_colors = int(request.form.get("colors", 24))

        result_img = generate_paint_by_numbers(image, num_colors=num_colors)

        # Full version for download
        full_io = io.BytesIO()
        result_img.save(full_io, format="PNG")
        full_io.seek(0)

        # Small version for preview
        preview_img = result_img.copy()
        preview_img.thumbnail((400, 400))
        preview_io = io.BytesIO()
        preview_img.save(preview_io, format="PNG")
        preview_b64 = base64.b64encode(preview_io.getvalue()).decode("utf-8")

        return jsonify({
            "preview": f"data:image/png;base64,{preview_b64}"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/")
def home():
    return "✅ Paint-by-Numbers Generator draait."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
