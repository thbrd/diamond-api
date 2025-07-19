
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from sklearn.cluster import KMeans
import cv2

def paint_to_numbers(image_pil, n_colors=24, max_regions=200):
    image = np.array(image_pil)
    h, w = image.shape[:2]
    flat = image.reshape((-1, 3))
    kmeans = KMeans(n_clusters=n_colors, n_init=5, random_state=0)
    kmeans.fit(flat)
    labels = kmeans.labels_.reshape(h, w)
    palette = np.round(kmeans.cluster_centers_).astype(np.uint8)

    merged = cv2.medianBlur(labels.astype(np.uint8), 3)
    num_labels, labeled = cv2.connectedComponents(merged)

    output = Image.new("RGB", (w, h), (255, 255, 255))
    draw = ImageDraw.Draw(output)
    font = None
    try:
        font = ImageFont.truetype("arial.ttf", 10)
    except:
        pass

    region_map = {}
    for region_id in range(num_labels):
        mask = (labeled == region_id)
        coords = np.column_stack(np.where(mask))
        if coords.size == 0:
            continue
        avg_color = palette[labels[coords[0][0], coords[0][1]]]
        for y, x in coords:
            output.putpixel((x, y), tuple(avg_color))
        y_mean, x_mean = np.mean(coords, axis=0).astype(int)
        if font:
            draw.text((x_mean, y_mean), str(region_id + 1), fill=(0, 0, 0), font=font)
        else:
            draw.text((x_mean, y_mean), str(region_id + 1), fill=(0, 0, 0))
        region_map[region_id + 1] = tuple(avg_color)

    output = output.resize((w * 10, h * 10), Image.NEAREST)
    return output, region_map
