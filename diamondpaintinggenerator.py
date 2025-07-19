
from PIL import Image, ImageDraw
import numpy as np
import json

with open("dmc_colors.json") as f:
    DMC_COLORS = json.load(f)
DMC_RGB = np.array([d["rgb"] for d in DMC_COLORS])

def suggest_best_canvas_format(image, dpi_per_mm=4, max_stones=100_000):
    img_w, img_h = image.size
    aspect_ratio = img_w / img_h
    base_height_mm = 400
    base_width_mm = int(base_height_mm * aspect_ratio)
    stones_w = int(base_width_mm * dpi_per_mm / 10)
    stones_h = int(base_height_mm * dpi_per_mm / 10)
    total = stones_w * stones_h
    if total > max_stones:
        scale = (max_stones / total) ** 0.5
        stones_w = int(stones_w * scale)
        stones_h = int(stones_h * scale)
        base_width_mm = int(stones_w * 10 / dpi_per_mm)
        base_height_mm = int(stones_h * 10 / dpi_per_mm)
    w_cm = round(base_width_mm / 10)
    h_cm = round(base_height_mm / 10)
    return (w_cm, h_cm), (stones_w, stones_h)

def map_to_dmc(image, width, height, stone_size=10, shape="square"):
    small = image.resize((width, height), Image.Resampling.BICUBIC)
    small_pixels = np.array(small).reshape(-1, 3)
    mapped_pixels = []
    used_codes = set()
    for pixel in small_pixels:
        dists = np.linalg.norm(DMC_RGB - pixel, axis=1)
        nearest = np.argmin(dists)
        mapped_pixels.append(DMC_RGB[nearest])
        used_codes.add(nearest)
    mapped = np.array(mapped_pixels, dtype=np.uint8).reshape(height, width, 3)
    used_codes = sorted(list(used_codes))
    canvas = Image.new("RGB", (width * stone_size, height * stone_size), (255, 255, 255))
    draw = ImageDraw.Draw(canvas)
    for y in range(height):
        for x in range(width):
            color = tuple(mapped[y, x])
            rect = [x * stone_size, y * stone_size, (x + 1) * stone_size, (y + 1) * stone_size]
            if shape == "round":
                draw.ellipse(rect, fill=color, outline=(200, 200, 200))
            else:
                draw.rectangle(rect, fill=color, outline=(200, 200, 200))
    return canvas, used_codes, width, height

def generate_diamond_painting(image, shape="square"):
    (canvas_w, canvas_h), (stones_w, stones_h) = suggest_best_canvas_format(image)
    result, codes, w, h = map_to_dmc(image, stones_w, stones_h, shape=shape)
    return result, {"canvas_cm": f"{canvas_w}x{canvas_h}", "stones": f"{w}x{h}"}
