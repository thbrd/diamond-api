import numpy as np
from PIL import Image, ImageDraw, ImageFont
import json
import uuid
import os
import cv2
from sklearn.cluster import KMeans

def generate_paint_by_numbers(image, num_colors, static_folder="static"):
    uid = str(uuid.uuid4())
    os.makedirs(static_folder, exist_ok=True)

    original_size = image.size
    img = image.copy()
    MAX_ANALYZE_SIZE = 400
    img.thumbnail((MAX_ANALYZE_SIZE, MAX_ANALYZE_SIZE), Image.Resampling.BICUBIC)

    np_img = np.array(img)
    pixels = np_img.reshape(-1, 3)

    kmeans = KMeans(n_clusters=num_colors, random_state=42).fit(pixels)
    labels = kmeans.labels_.reshape(np_img.shape[0], np_img.shape[1])
    centers = np.round(kmeans.cluster_centers_).astype(np.uint8)

    # Maak kleur-gebaseerde output afbeelding (PNG)
    color_img = np.zeros_like(np_img)
    for i in range(num_colors):
        color_img[labels == i] = centers[i]

    color_pil = Image.fromarray(color_img)
    color_pil_up = color_pil.resize(original_size, Image.NEAREST)
    png_path = os.path.join(static_folder, f"{uid}.png")
    color_pil_up.save(png_path, format="PNG")

    # SVG genereren met contouren en nummers
    gray_labels = (labels / num_colors * 255).astype(np.uint8)
    contours, _ = cv2.findContours(gray_labels, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    scale_x = original_size[0] / img.width
    scale_y = original_size[1] / img.height

    svg = f"<svg xmlns='http://www.w3.org/2000/svg' width='{original_size[0]}' height='{original_size[1]}' viewBox='0 0 {original_size[0]} {original_size[1]}'>"
    svg += "<style>text{font-size:10px;fill:black;}</style>"

    for y in range(0, labels.shape[0], 10):
        for x in range(0, labels.shape[1], 10):
            label = str(int(labels[y, x]) + 1)
            sx = int(x * scale_x)
            sy = int(y * scale_y)
            svg += f"<text x='{sx}' y='{sy}'>{label}</text>"

    for cnt in contours:
        path = "M "
        for point in cnt:
            x, y = point[0]
            sx = int(x * scale_x)
            sy = int(y * scale_y)
            path += f"{sx},{sy} "
        svg += f"<path d='{path.strip()}' fill='none' stroke='black' stroke-width='0.5'/>"

    svg += "</svg>"
    svg_path = os.path.join(static_folder, f"{uid}.svg")
    with open(svg_path, "w", encoding="utf-8") as f:
        f.write(svg)

    return uid