import numpy as np
from PIL import Image, ImageDraw, ImageFont
import cv2
import uuid
import os
from sklearn.cluster import KMeans

def generate_paint_by_numbers(image, num_colors, static_folder="static"):
    uid = str(uuid.uuid4())
    os.makedirs(static_folder, exist_ok=True)

    original_size = image.size
    img = image.copy()
    MAX_ANALYZE_SIZE = 400
    img.thumbnail((MAX_ANALYZE_SIZE, MAX_ANALYZE_SIZE), Image.Resampling.BICUBIC)
    width, height = img.size

    np_img = np.array(img)
    flat_img = np_img.reshape(-1, 3)

    kmeans = KMeans(n_clusters=num_colors, random_state=42).fit(flat_img)
    labels = kmeans.labels_.reshape(height, width)
    centers = np.round(kmeans.cluster_centers_).astype(np.uint8)

    # PNG-output met kleurvlakken + nummers
    color_img = np.zeros((height, width, 3), dtype=np.uint8)
    for i in range(num_colors):
        color_img[labels == i] = centers[i]

    png_pil = Image.fromarray(color_img).resize(original_size, Image.NEAREST)
    draw = ImageDraw.Draw(png_pil)
    try:
        font = ImageFont.load_default()
    except Exception:
        font = None

    for y in range(0, height, 10):
        for x in range(0, width, 10):
            label = str(labels[y][x] + 1)
            sx = int(x * original_size[0] / width)
            sy = int(y * original_size[1] / height)
            if font:
                draw.text((sx, sy), label, fill="black", font=font)

    png_path = os.path.join(static_folder, f"{uid}.png")
    png_pil.save(png_path, format="PNG")

    # SVG-output met gekleurde paden
    svg = f"<svg xmlns='http://www.w3.org/2000/svg' width='{original_size[0]}' height='{original_size[1]}' viewBox='0 0 {original_size[0]} {original_size[1]}'>"
    svg += "<style>text{font-size:10px;fill:black;} path{stroke:black;stroke-width:0.5;}</style>"

    scale_x = original_size[0] / width
    scale_y = original_size[1] / height

    for i in range(num_colors):
        mask = (labels == i).astype(np.uint8) * 255
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        hex_color = '#%02x%02x%02x' % tuple(centers[i])
        for cnt in contours:
            path_d = "M " + " ".join(f"{int(p[0][0]*scale_x)},{int(p[0][1]*scale_y)}" for p in cnt)
            svg += f"<path d='{path_d}' fill='{hex_color}'/>"

    for y in range(0, height, 10):
        for x in range(0, width, 10):
            label = str(labels[y][x] + 1)
            sx = int(x * scale_x)
            sy = int(y * scale_y)
            svg += f"<text x='{sx}' y='{sy}'>{label}</text>"

    svg += "</svg>"
    svg_path = os.path.join(static_folder, f"{uid}.svg")
    with open(svg_path, "w", encoding="utf-8") as f:
        f.write(svg)

    return uid