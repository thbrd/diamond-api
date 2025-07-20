from PIL import Image, ImageDraw, ImageFont
import numpy as np
import cv2
from sklearn.cluster import KMeans
import json
from pathlib import Path

PALETTE = json.load(open(str(Path(__file__).parent / "paint_colors.json")))

def closest_color(rgb, palette):
    return min(palette, key=lambda c: sum((rgb[i] - c[i]) ** 2 for i in range(3)))

def generate_paint_by_numbers(input_image, color_count=24):
    image = input_image.copy().convert("RGB")
    img_array = np.array(image)
    pixels = img_array.reshape((-1, 3))

    kmeans = KMeans(n_clusters=color_count, random_state=0).fit(pixels)
    clustered = kmeans.cluster_centers_[kmeans.labels_].reshape(img_array.shape).astype('uint8')

    simplified_img = Image.fromarray(clustered)

    gray = cv2.cvtColor(clustered, cv2.COLOR_RGB2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    edges_inv = cv2.bitwise_not(edges)
    numbered_img = Image.fromarray(edges_inv).convert("RGB")
    draw = ImageDraw.Draw(numbered_img)
    font = ImageFont.load_default()

    labels = kmeans.labels_.reshape((img_array.shape[0], img_array.shape[1]))
    centers = kmeans.cluster_centers_.astype(int)

    for i in range(0, labels.shape[0], 25):
        for j in range(0, labels.shape[1], 25):
            label = labels[i, j]
            draw.text((j, i), str(label + 1), fill=(0, 0, 0), font=font)

    swatch_size = 50
    color_map = Image.new("RGB", (swatch_size * color_count, swatch_size), "white")
    draw = ImageDraw.Draw(color_map)
    for idx, color in enumerate(centers):
        x0 = idx * swatch_size
        draw.rectangle([x0, 0, x0 + swatch_size, swatch_size], fill=tuple(color))

    return simplified_img, numbered_img, color_map