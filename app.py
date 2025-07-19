
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

STATIC_DIR = os.path.join(os.path.dirname(__file__), "..", "web", "static")
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
app = Flask(__name__, static_folder="static")
app.secret_key = "supersecretkey"
CORS(app)

@app.route("/process-numbers", methods=["POST"])
def process_numbers():
    if "image" not in request.files:
        return jsonify({"error": "No image provided"}), 400
    base_url = "http://91.98.21.195:5000"
        return jsonify({
            "canvas": f"{base_url}/static/{canvas_filename}",
            "painted": f"{base_url}/static/{painted_filename}",
            "download_canvas": f"{base_url}/static/{canvas_filename}",
            "download_painted": f"{base_url}/static/{painted_filename}"
        return jsonify({"error": "No image provided"}), 400
    try:
        file = request.files["image"]
        image = Image.open(file.stream).convert("RGB")
        num_colors = int(request.form.get("colors", 24))

        log_request("paintbynumbers")
        canvas_img, painted_img = generate_paint_by_numbers(image, num_colors)

        unique_id = str(uuid.uuid4())
        canvas_filename = f"canvas_{unique_id}.png"
        painted_filename = f"painted_{unique_id}.png"
        canvas_path = os.path.join(STATIC_DIR, canvas_filename)
        painted_path = os.path.join(STATIC_DIR, painted_filename)
        canvas_img.save(canvas_path)
        painted_img.save(painted_path)

        canvas_preview = canvas_img.copy()
        painted_preview = painted_img.copy()
        canvas_preview.thumbnail((600, 600))
        painted_preview.thumbnail((600, 600))

        canvas_io = io.BytesIO()
        canvas_preview.save(canvas_io, format="PNG")
        canvas_b64 = base64.b64encode(canvas_io.getvalue()).decode("utf-8")

        painted_io = io.BytesIO()
        painted_preview.save(painted_io, format="PNG")
        painted_b64 = base64.b64encode(painted_io.getvalue()).decode("utf-8")

    base_url = "http://91.98.21.195:5000"
        return jsonify({
            "canvas": f"{base_url}/static/{canvas_filename}",
            "painted": f"{base_url}/static/{painted_filename}",
            "download_canvas": f"{base_url}/static/{canvas_filename}",
            "download_painted": f"{base_url}/static/{painted_filename}"
        })
            "canvas": f"data:image/png;base64,{canvas_b64}",
            "painted": f"data:image/png;base64,{painted_b64}",
            "download_canvas": f"/static/{canvas_filename}",
            "download_painted": f"/static/{painted_filename}"
        })
    except Exception as e:
    base_url = "http://91.98.21.195:5000"
        return jsonify({
            "canvas": f"{base_url}/static/{canvas_filename}",
            "painted": f"{base_url}/static/{painted_filename}",
            "download_canvas": f"{base_url}/static/{canvas_filename}",
            "download_painted": f"{base_url}/static/{painted_filename}"
        })"error": f"Fout tijdens verwerking: {str(e)}"}), 500

@app.route("/logs")
def logs():
    return jsonify(get_logs())

@app.route("/cleanup")
def cleanup():
    removed = clear_generated_files()
    return jsonify({
            "canvas": f"{base_url}/static/{canvas_filename}",
            "painted": f"{base_url}/static/{painted_filename}",
            "download_canvas": f"{base_url}/static/{canvas_filename}",
            "download_painted": f"{base_url}/static/{painted_filename}"
        })"removed_files": removed})

@app.route("/admin")
def admin():
    if not session.get("logged_in"):
        return redirect("/login")
    return send_file("../web/admin.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form.get("username") == "admin" and request.form.get("password") == "happyhobby":
            session["logged_in"] = True
            return redirect("/admin")
        return "❌ Ongeldige inloggegevens", 403
    return send_file("../web/login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/")
def home():
    return "✅ HappyHobby backend draait"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
