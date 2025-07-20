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
        return jsonify({"error": "No image provided"}), 400
    try:
        file = request.files["image"]
        image = Image.open(file.stream).convert("RGB")
        raw_colors = request.form.get("colors")
        try:
            num_colors = int(raw_colors)
        except (ValueError, TypeError):
            num_colors = 24

        log_request("paintbynumbers")
        canvas_img = generate_paint_by_numbers(image, num_colors)

        unique_id = str(uuid.uuid4())
        canvas_filename = f"canvas_{unique_id}.png"
        painted_filename = f"painted_{unique_id}.png"
        canvas_path = os.path.join(STATIC_DIR, canvas_filename)
        painted_path = os.path.join(STATIC_DIR, painted_filename)
        canvas_img.save(os.path.join(STATIC_DIR, "preview.png"))
        
        base_url = "http://91.98.21.195:5000"
        return jsonify({
            "preview": f"{base_url}/static/preview.png",
                                            })
    except Exception as e:
        return jsonify({"error": f"Fout tijdens verwerking: {str(e)}"}), 500

@app.route("/logs")
def logs():
    return jsonify(get_logs())

@app.route("/cleanup")
def cleanup():
    removed = clear_generated_files()
    return jsonify({"removed_files": removed})

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



@app.route("/process-diamond", methods=["POST"])
def process_diamond():
    if "image" not in request.files:
        return jsonify({"error": "No image provided"}), 400
    try:
        file = request.files["image"]
        image = Image.open(file.stream).convert("RGB")
        shape = request.form.get("shape", "square")
        if shape not in ["round", "square"]:
            shape = "square"

        log_request("diamondpainting")
        canvas_img, _ = generate_diamond_painting(image, shape=shape)

        unique_id = str(uuid.uuid4())
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"preview_{timestamp}_{unique_id}.png"
        path = os.path.join(STATIC_DIR, filename)
        canvas_img.save(path)

        base_url = "http://91.98.21.195:5000"
        return jsonify({
            "preview": f"{base_url}/static/{filename}"
        })
    except Exception as e:
        return jsonify({"error": f"Fout tijdens verwerking: {str(e)}"}), 500
