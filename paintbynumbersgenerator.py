
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
for label_val in range(num_colors):
        mask = np.uint8(label_image == label_val)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for cnt in contours:
            if cv2.contourArea(cnt) < 50:
                continue

            # Draw contour
            cv2.drawContours(contour_img, [cnt], -1, (0, 0, 0), line_thickness, cv2.LINE_AA)

            # Get center of contour and label
            M = cv2.moments(cnt)
            if M["m00"] != 0:
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
                cv2.putText(contour_img, str(label_val + 1), (cX - 5 * scale_multiplier, cY + 5 * scale_multiplier), font, font_scale, (0, 0, 0), line_thickness, cv2.LINE_AA)

            contour_img = cv2.cvtColor(contour_img, cv2.COLOR_BGR2RGB)
            # === Vergelijkbaar met svgSizeMultiplier: verhoog resolutie van eindresultaat ===
        scale_multiplier = 3
        upscaled = cv2.resize(contour_img, (contour_img.shape[1]*scale_multiplier, contour_img.shape[0]*scale_multiplier), interpolation=cv2.INTER_NEAREST)
        return Image.fromarray(upscaled)
