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

    # PNG: kleurvlakken + nummers + contouren
    png_img = Image.new("RGB", (width, height))
    draw = ImageDraw.Draw(png_img)

    try:
        font = ImageFont.load_default()
    except Exception:
        font = None

    for i in range(num_colors):
        mask = (labels == i).astype(np.uint8) * 255
        color = tuple(centers[i])
        for y in range(height):
            for x in range(width):
                if labels[y][x] == i:
                    png_img.putpixel((x, y), color)

        # Tekst op centroid
        moments = cv2.moments(mask)
        if moments["m00"] != 0:
            cx = int(moments["m10"] / moments["m00"])
            cy = int(moments["m01"] / moments["m00"])
            if font:
                draw.text((cx, cy), str(i + 1), fill="black", font=font)

        # Contouren tekenen
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in contours:
            points = [(int(p[0][0]), int(p[0][1])) for p in cnt]
            if len(points) > 2:
                draw.line(points + [points[0]], fill="black", width=1)

    png_up = png_img.resize(original_size, Image.NEAREST)
    png_path = os.path.join(static_folder, f"{uid}.png")
    png_up.save(png_path)

    # SVG: kleurvlak + path + tekst op centroid
    svg = f"<svg xmlns='http://www.w3.org/2000/svg' width='{original_size[0]}' height='{original_size[1]}' viewBox='0 0 {original_size[0]} {original_size[1]}'>"
    svg += "<style>text{font-size:10px;fill:black;} path{stroke:black;stroke-width:0.5;}</style>"

    scale_x = original_size[0] / width
    scale_y = original_size[1] / height

    for i in range(num_colors):
        mask = (labels == i).astype(np.uint8) * 255
        hex_color = '#%02x%02x%02x' % tuple(centers[i])

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in contours:
            if len(cnt) < 3:
                continue
            path_d = "M " + " ".join(f"{int(p[0][0]*scale_x)},{int(p[0][1]*scale_y)}" for p in cnt)
            svg += f"<path d='{path_d}' fill='{hex_color}'/>"

        # Tekst op centroid
        moments = cv2.moments(mask)
        if moments["m00"] != 0:
            cx = int((moments["m10"] / moments["m00"]) * scale_x)
            cy = int((moments["m01"] / moments["m00"]) * scale_y)
            svg += f"<text x='{cx}' y='{cy}'>{i + 1}</text>"

    svg += "</svg>"
    svg_path = os.path.join(static_folder, f"{uid}.svg")
    with open(svg_path, "w", encoding="utf-8") as f:
        f.write(svg)

    return uid