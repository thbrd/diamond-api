
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont

def generate_paint_by_numbers(image: Image.Image, num_colors: int = 24) -> Image.Image:
    image = image.convert("RGB")
    img = np.array(image)
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    Z = img.reshape((-1, 3))
    Z = np.float32(Z)

    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    _, labels, centers = cv2.kmeans(Z, num_colors, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)

    centers = np.uint8(centers)
    res = centers[labels.flatten()]
    clustered_img = res.reshape((img.shape))
    clustered_img = cv2.cvtColor(clustered_img, cv2.COLOR_BGR2RGB)

    label_img = labels.reshape((img.shape[0], img.shape[1]))
    canvas = Image.fromarray(clustered_img)
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.load_default()

    step = max(1, min(img.shape[:2]) // 40)
    for y in range(0, img.shape[0], step):
        for x in range(0, img.shape[1], step):
            label = label_img[y, x]
            draw.text((x, y), str(label + 1), font=font, fill=(0, 0, 0))

    return canvas
