from flask import Flask, request, jsonify
from io import BytesIO
import base64
from PIL import Image
from paintbynumbersgenerator import generate_paint_by_numbers

app = Flask(__name__)

@app.route('/generate-pbn', methods=['POST'])
def generate_pbn():
    if 'image' not in request.files or 'colors' not in request.form:
        return jsonify({'error': 'Image and color count are required.'}), 400

    try:
        color_count = int(request.form['colors'])
    except ValueError:
        return jsonify({'error': 'Invalid color count.'}), 400

    if color_count not in (24, 36, 48):
        return jsonify({'error': 'Invalid color count. Only 24, 36, or 48 allowed.'}), 400

    img = Image.open(request.files['image']).convert("RGB")
    simplified, numbered, color_map = generate_paint_by_numbers(img, color_count)

    def img_to_base64(image):
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        return "data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode()

    return jsonify({
        'simplified': img_to_base64(simplified),
        'numbered': img_to_base64(numbered),
        'color_map': img_to_base64(color_map)
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
