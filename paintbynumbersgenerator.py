
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import json
import io
import base64
import os

with open("paint_colors.json") as f:
    PALETTE = json.load(f)

def generate_paint_by_numbers_svg_png(image, num_colors):
    colors = PALETTE[str(num_colors)]
    palette = np.array(colors)

    # Resize image to max 80x80 (zoals originele repo)
    w, h = image.size
    ratio = 80 / max(w, h)
    image = image.resize((int(w * ratio), int(h * ratio)))
    np_img = np.array(image)

    # Map naar dichtstbijzijnde kleur
    reshaped = np_img.reshape(-1, 3)
    distances = np.linalg.norm(palette[None, :, :] - reshaped[:, None, :], axis=2)
    labels = np.argmin(distances, axis=1).reshape(np_img.shape[:2])

    h, w = labels.shape
    cell_size = 20
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w*cell_size}" height="{h*cell_size}">']

    for y in range(h):
        for x in range(w):
            color = palette[labels[y, x]]
            svg.append(f'<rect x="{x*cell_size}" y="{y*cell_size}" width="{cell_size}" height="{cell_size}" fill="rgb{tuple(color)}" stroke="#000" stroke-width="0.5"/>')
            svg.append(f'<text x="{x*cell_size+cell_size/2}" y="{y*cell_size+cell_size/2}" text-anchor="middle" dominant-baseline="central" font-size="8" fill="#000">{labels[y, x]+1}</text>')

    svg.append("</svg>")
    svg_str = "".join(svg)

    # PNG render voor download
    img = Image.new("RGB", (w * cell_size, h * cell_size), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()
    for y in range(h):
        for x in range(w):
            color = tuple(palette[labels[y, x]])
            rect = [x * cell_size, y * cell_size, (x + 1) * cell_size, (y + 1) * cell_size]
            draw.rectangle(rect, fill=color, outline=(0, 0, 0))
            draw.text((rect[0]+cell_size//3, rect[1]+cell_size//3), str(labels[y, x]+1), fill=(0, 0, 0), font=font)

    return svg_str, img
