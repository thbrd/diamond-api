
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import cv2

def paint_by_numbers(image, num_colors=24):
    img = np.array(image)
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    Z = img.reshape((-1, 3))
    Z = np.float32(Z)

    # KMeans clustering
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    _, labels, centers = cv2.kmeans(Z, num_colors, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
    centers = np.uint8(centers)
    res = centers[labels.flatten()]
    clustered = res.reshape((img.shape))
    clustered_rgb = cv2.cvtColor(clustered, cv2.COLOR_BGR2RGB)

    # Genummerd canvas genereren
    label_img = labels.reshape((img.shape[0], img.shape[1]))
    canvas = np.ones_like(clustered_rgb) * 255  # wit canvas

    font = ImageFont.load_default()
    label_numbers = label_img // (label_img.max() + 1) * num_colors
    step = max(1, min(canvas.shape[0], canvas.shape[1]) // 100)

    pil_canvas = Image.fromarray(canvas)
    draw = ImageDraw.Draw(pil_canvas)
    for y in range(0, canvas.shape[0], step):
        for x in range(0, canvas.shape[1], step):
            idx = label_img[y, x]
            draw.text((x, y), str(idx + 1), fill=(0, 0, 0), font=font)

    painted_img = Image.fromarray(clustered_rgb)
    return painted_img, pil_canvas
