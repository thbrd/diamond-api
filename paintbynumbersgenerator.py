import numpy as np
from PIL import Image, ImageDraw, ImageFont
import cv2
import uuid
import os
from sklearn.cluster import KMeans

def generate_paint_by_numbers(image, num_colors, static_folder="static"):
    uid = str(uuid.uuid4())
    os.makedirs(static_folder, exist_ok=True)

    original_w, original_h = image.size
    small_img = image.copy()
    small_img.thumbnail((400, 400), Image.Resampling.BICUBIC)
    small_w, small_h = small_img.size

    np_small = np.array(small_img)
    pixels = np_small.reshape(-1, 3)
    kmeans = KMeans(n_clusters=num_colors, random_state=42).fit(pixels)
    centers = np.clip(np.round(kmeans.cluster_centers_), 0, 255).astype(np.uint8)
    labels_small = kmeans.labels_.reshape(small_h, small_w)

    labels_up = cv2.resize(labels_small.astype(np.uint8), (original_w, original_h), interpolation=cv2.INTER_NEAREST)

    # Small facet pruning: filter tiny masks
    def filter_small(mask, min_area=100):
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        filtered = np.zeros_like(mask)
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area >= min_area:
                cv2.drawContours(filtered, [cnt], -1, 255, -1)
        return filtered

    # PNG
    png_img = Image.new("RGB", (original_w, original_h), "white")
    draw = ImageDraw.Draw(png_img)
    font_size = max(10, original_w // 100)
    font = ImageFont.truetype("arial.ttf", font_size)

    for i in range(num_colors):
        mask = (labels_up == i).astype(np.uint8) * 255
        mask = filter_small(mask)
        color = tuple(centers[i])

        for y in range(original_h):
            for x in range(original_w):
                if mask[y][x] == 255:
                    png_img.putpixel((x, y), color)

        # contour
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in contours:
            approx = cv2.approxPolyDP(cnt, epsilon=2, closed=True)
            if len(approx) > 2:
                points = [(int(p[0][0]), int(p[0][1])) for p in approx]
                draw.line(points + [points[0]], fill="black", width=1)

        # centroid
        m = cv2.moments(mask)
        if m["m00"] != 0:
            cx = int(m["m10"] / m["m00"])
            cy = int(m["m01"] / m["m00"])
            draw.text((cx, cy), str(i + 1), fill="black", font=font)

    png_path = os.path.join(static_folder, f"{uid}.png")
    png_img.save(png_path)

    # SVG
    svg = f"<svg xmlns='http://www.w3.org/2000/svg' width='{original_w}' height='{original_h}' viewBox='0 0 {original_w} {original_h}'>"
    svg += "<style>text{font-size:10px;fill:black;} path{stroke:black;stroke-width:0.3;}</style>"

    for i in range(num_colors):
        mask = (labels_up == i).astype(np.uint8) * 255
        mask = filter_small(mask)
        hex_color = '#%02x%02x%02x' % tuple(centers[i])

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in contours:
            approx = cv2.approxPolyDP(cnt, epsilon=2, closed=True)
            if len(approx) > 2:
                d = "M " + " ".join(f"{int(p[0][0])},{int(p[0][1])}" for p in approx)
                svg += f"<path d='{d}' fill='{hex_color}'/>"

        m = cv2.moments(mask)
        if m["m00"] != 0:
            cx = int(m["m10"] / m["m00"])
            cy = int(m["m01"] / m["m00"])
            svg += f"<text x='{cx}' y='{cy}'>{i + 1}</text>"

    svg += "</svg>"
    svg_path = os.path.join(static_folder, f"{uid}.svg")
    with open(svg_path, "w", encoding="utf-8") as f:
        f.write(svg)

    return uid