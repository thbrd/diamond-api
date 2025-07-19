
from PIL import Image, ImageDraw
import numpy as np
import json

with open("dmc_colors.json") as f:
    DMC_COLORS = json.load(f)
DMC_RGB = np.array([d["rgb"] for d in DMC_COLORS])

def generate_diamond_painting(image, shape="square"):
    width, height = 100, 100
    resized = image.resize((width, height), Image.Resampling.BICUBIC)
    pixels = np.array(resized).reshape(-1, 3)
    result_pixels = []
    for pixel in pixels:
        dists = np.linalg.norm(DMC_RGB - pixel, axis=1)
        nearest = np.argmin(dists)
        result_pixels.append(DMC_RGB[nearest])
    mapped = np.array(result_pixels, dtype=np.uint8).reshape(height, width, 3)
    canvas = Image.new("RGB", (width * 10, height * 10), (255, 255, 255))
    draw = ImageDraw.Draw(canvas)
    for y in range(height):
        for x in range(width):
            color = tuple(mapped[y, x])
            rect = [x * 10, y * 10, (x + 1) * 10, (y + 1) * 10]
            if shape == "round":
                draw.ellipse(rect, fill=color, outline=(200, 200, 200))
            else:
                draw.rectangle(rect, fill=color, outline=(200, 200, 200))
    return canvas, {"size": f"{width}x{height}"}
