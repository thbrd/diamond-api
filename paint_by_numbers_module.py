
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont


def paint_by_numbers(image, num_colors=24):
    # Resize for processing speed
    image = image.resize((300, 300), Image.LANCZOS)
    img = np.array(image)
    img_bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    Z = img_bgr.reshape((-1, 3)).astype(np.float32)

    # KMeans
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    _, labels, centers = cv2.kmeans(Z, num_colors, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)

    centers = np.uint8(centers)
    res = centers[labels.flatten()]
    clustered_img = res.reshape((img.shape))
    clustered_rgb = cv2.cvtColor(clustered_img, cv2.COLOR_BGR2RGB)

    # Canvas
    label_img = labels.reshape((img.shape[0], img.shape[1]))
    canvas = np.full_like(clustered_rgb, 255)

    pil_canvas = Image.fromarray(canvas)
    draw = ImageDraw.Draw(pil_canvas)
    font = ImageFont.load_default()

    step = max(1, min(img.shape[:2]) // 40)
    for y in range(0, img.shape[0], step):
        for x in range(0, img.shape[1], step):
            label = label_img[y, x]
            draw.text((x, y), str(label + 1), font=font, fill=(0, 0, 0))

    painted_img = Image.fromarray(clustered_rgb)
    return painted_img, pil_canvas
