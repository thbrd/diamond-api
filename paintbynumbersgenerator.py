import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont
def generate_paint_by_numbers(image: Image.Image, num_colors: int = 24) -> Image.Image:
    image = image.convert("RGB")
    img = np.array(image)
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

    # Rescale image for clustering
    max_size = 1024  # Langste zijde max, behoud aspect ratio
    if max(img.shape[:2]) > max_size:
        scale = max_size / max(img.shape[:2])
        
    h, w = img.shape[:2]
    if max(h, w) > max_size:
        scale = max_size / max(h, w)
        new_w = int(w * scale)
        new_h = int(h * scale)


    Z = img.reshape((-1, 3))
    Z = np.float32(Z)

    # KMeans clustering
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    _, labels, centers = cv2.kmeans(Z, num_colors, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)

    centers = np.uint8(centers)
    res = centers[labels.flatten()]
    clustered_img = res.reshape((img.shape))

    # Create mask for each label
    label_image = labels.reshape((img.shape[0], img.shape[1]))
    contour_img = clustered_img.copy()
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.4 * scale_multiplier
    line_thickness = int(1 * scale_multiplier)
        scale_multiplier = 3
        upscaled = cv2.resize(contour_img, (contour_img.shape[1]*scale_multiplier, contour_img.shape[0]*scale_multiplier), interpolation=cv2.INTER_NEAREST)
        return Image.fromarray(upscaled)
