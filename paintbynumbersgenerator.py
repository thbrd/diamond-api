from PIL import Image, ImageDraw, ImageFont
import numpy as np
import cv2
from sklearn.cluster import KMeans

def generate_paint_by_numbers(input_path, output_path, num_colors=24):
    img = Image.open(input_path).convert("RGB")
    img = img.resize((800, 800))  # consistent grotere preview

    img_np = np.array(img)
    h, w, _ = img_np.shape
    img_flat = img_np.reshape((-1, 3))

    kmeans = KMeans(n_clusters=num_colors, n_init="auto")
    labels = kmeans.fit_predict(img_flat)
    palette = np.uint8(kmeans.cluster_centers_)
    quantized = palette[labels].reshape((h, w, 3))

    contour_img = quantized.copy()
    gray = cv2.cvtColor(quantized, cv2.COLOR_RGB2GRAY)
    edges = cv2.Canny(gray, 100, 200)
    contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(contour_img, contours, -1, (0, 0, 0), 1)

    numbered_img = Image.fromarray(contour_img)
    draw = ImageDraw.Draw(numbered_img)
    font = ImageFont.load_default()

    label_image = labels.reshape((h, w))
    for i in range(0, h, 30):
        for j in range(0, w, 30):
            region = label_image[i:i+30, j:j+30]
            if region.size == 0: continue
            label = int(np.median(region))
            draw.text((j+10, i+10), str(label+1), fill="black", font=font)

    numbered_img.save(output_path)