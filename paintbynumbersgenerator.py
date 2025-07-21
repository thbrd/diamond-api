import numpy as np
from PIL import Image, ImageDraw, ImageFont
import json
import uuid
import os

with open("paint_colors.json", "r") as f:
    COLOR_PALETTES = json.load(f)

def generate_paint_by_numbers(image, num_colors, static_folder="static"):
    palette = np.array(COLOR_PALETTES[str(num_colors)])
    img = image.convert("RGB")
    width, height = img.size
    img_np = np.array(img).reshape(-1, 3)

    diffs = np.linalg.norm(img_np[:, None, :] - palette[None, :, :], axis=2)
    closest = np.argmin(diffs, axis=1)
    labels = closest.reshape((height, width))
    remapped = palette[labels]

    color_img = Image.fromarray(remapped.astype(np.uint8))
    number_img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(number_img)
    font = ImageFont.load_default()

    for y in range(0, height, 10):
        for x in range(0, width, 10):
            label = str(int(labels[y][x]) + 1)
            draw.text((x, y), label, fill="black", font=font)

    # SVG-bestand genereren
    svg = f"<svg xmlns='http://www.w3.org/2000/svg' width='{width}' height='{height}'>"
    for y in range(0, height, 10):
        for x in range(0, width, 10):
            label = str(int(labels[y][x]) + 1)
            svg += f"<text x='{x}' y='{y + 8}' font-size='10' fill='black'>{label}</text>"
    svg += "</svg>"

    uid = str(uuid.uuid4())
    svg_path = os.path.join(static_folder, f"{uid}.svg")
    png_path = os.path.join(static_folder, f"{uid}.png")

    with open(svg_path, "w") as f:
        f.write(svg)

    color_img.save(png_path, format="PNG")

    return uid