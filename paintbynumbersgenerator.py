from PIL import Image, ImageDraw, ImageFont
import numpy as np
import json
import random

with open("paint_colors.json", "r") as f:
    COLOR_PALETTES = json.load(f)

def generate_paint_by_numbers(image, num_colors=24):
    image = image.resize((100, 100), Image.Resampling.BILINEAR)
    img_array = np.array(image)

    colors = COLOR_PALETTES[str(num_colors)]
    palette = np.array(colors)
    img_flat = img_array.reshape(-1, 3)

    # Bereken afstand tot alle kleuren
    diffs = np.linalg.norm(img_flat[:, None, :] - palette[None, :, :], axis=2)
    closest = np.argmin(diffs, axis=1)
    labels = closest.reshape(img_array.shape[:2])
    indexed_img = palette[labels]

    # SVG-achtige nummering op canvas
    preview = Image.new("RGB", image.size, "white")
    draw = ImageDraw.Draw(preview)
    font = ImageFont.load_default()

    for y in range(labels.shape[0]):
        for x in range(labels.shape[1]):
            color = tuple(indexed_img[y, x])
            label = int(labels[y, x]) + 1
            preview.putpixel((x, y), color)
            if x % 10 == 0 and y % 10 == 0:
                draw.text((x, y), str(label), fill="black", font=font)

    return preview