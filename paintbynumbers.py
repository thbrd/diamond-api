
from PIL import Image, ImageDraw
import numpy as np

def generate_paint_by_numbers(image_path, n_colors):
    image = Image.open(image_path).convert("RGB").resize((300, 300))
    arr = np.array(image).reshape(-1, 3)
    unique_colors = np.linspace(0, 255, n_colors, dtype=np.uint8)
    bins = np.linspace(0, 255, n_colors + 1)
    quantized = np.digitize(arr, bins) - 1
    clustered = unique_colors[quantized].reshape(image.size[1], image.size[0], 3).astype(np.uint8)
    painted_img = Image.fromarray(clustered)

    canvas_img = Image.new("RGB", image.size, "white")
    draw = ImageDraw.Draw(canvas_img)
    for y in range(0, image.size[1], 10):
        for x in range(0, image.size[0], 10):
            draw.rectangle([x, y, x+10, y+10], outline="black")
            draw.text((x+2, y+2), str((x*y) % n_colors + 1), fill="black")

    return painted_img, canvas_img
