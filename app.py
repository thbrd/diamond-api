
from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import io
import base64
from paint_by_numbers_module import paint_by_numbers

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

        painted_img, canvas_img = paint_by_numbers(image, num_colors=num_colors)

        painted_io = io.BytesIO()
        canvas_io = io.BytesIO()
        painted_img.save(painted_io, format="PNG")
        canvas_img.save(canvas_io, format="PNG")

        painted_b64 = base64.b64encode(painted_io.getvalue()).decode("utf-8")
        canvas_b64 = base64.b64encode(canvas_io.getvalue()).decode("utf-8")

        return jsonify({
            "painted": f"data:image/png;base64,{painted_b64}",
            "canvas": f"data:image/png;base64,{canvas_b64}"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/")
def index():
    return "✅ Paint-by-Numbers API werkt"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
