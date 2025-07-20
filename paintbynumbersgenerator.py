
from sklearn.cluster import KMeans
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import cv2

def generate_paint_by_numbers(image, num_colors):
    img = image.resize((300, 300))
    img_np = np.array(img)

    data = img_np.reshape((-1, 3))
    kmeans = KMeans(n_clusters=num_colors, random_state=42).fit(data)
    labels = kmeans.labels_
    centers = kmeans.cluster_centers_.astype("uint8")

    clustered = centers[labels].reshape(img_np.shape)
    clustered_img = Image.fromarray(clustered)

    # Edge detection
    edges = cv2.Canny(cv2.cvtColor(clustered.astype("uint8"), cv2.COLOR_RGB2GRAY), 100, 200)
    edges_inv = cv2.bitwise_not(edges)
    edge_img = Image.fromarray(edges_inv).convert("L").convert("RGB")

    # Combine clustered image with edge overlay
    combined = Image.blend(clustered_img.convert("RGB"), edge_img, alpha=0.5)
    return combined
