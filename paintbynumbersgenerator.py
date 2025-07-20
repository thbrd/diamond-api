
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

def generate_paint_by_numbers(pil_image, num_colors):
    image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
    Z = image.reshape((-1, 3))
    Z = np.float32(Z)
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    K = num_colors
    _, labels, centers = cv2.kmeans(Z, K, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
    centers = np.uint8(centers)
    res = centers[labels.flatten()]
    clustered_image = res.reshape((image.shape))

    # Create painted image
    painted_image = Image.fromarray(cv2.cvtColor(clustered_image, cv2.COLOR_BGR2RGB))

    # Create canvas with numbers
    label_image = labels.reshape((image.shape[:2]))
    h, w = label_image.shape
    canvas = Image.new("RGB", (w, h), "white")
    draw = ImageDraw.Draw(canvas)

    font_size = max(10, min(w, h) // 100)
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        font = ImageFont.load_default()

    for y in range(0, h, font_size * 2):
        for x in range(0, w, font_size * 2):
            label = int(label_image[y][x])
            draw.text((x, y), str(label + 1), fill="black", font=font)

    # Detect edges and overlay on canvas
    gray = cv2.cvtColor(clustered_image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    edge_overlay = Image.fromarray(edges).convert("L")
    edge_overlay = edge_overlay.convert("RGBA")
    edge_overlay_data = edge_overlay.getdata()

    edge_overlay_data = [
        (0, 0, 0, 100) if pixel[0] > 0 else (0, 0, 0, 0)
        for pixel in edge_overlay_data
    ]
    edge_overlay.putdata(edge_overlay_data)
    canvas = canvas.convert("RGBA")
    canvas.alpha_composite(edge_overlay)

    return canvas.convert("RGB")
