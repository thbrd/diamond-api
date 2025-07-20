
import cv2
import numpy as np
from sklearn.cluster import KMeans
from PIL import Image

def generate_paint_by_numbers(pil_image, num_colors):
    image = np.array(pil_image)

    # Kleurreductie
    pixels = image.reshape(-1, 3)
    kmeans = KMeans(n_clusters=num_colors, random_state=42).fit(pixels)
    labels = kmeans.labels_
    clustered = kmeans.cluster_centers_.astype("uint8")[labels]
    clustered_image = clustered.reshape(image.shape)

    # Grijs voor contourdetectie
    gray = cv2.cvtColor(clustered_image, cv2.COLOR_RGB2GRAY)
    blurred = cv2.GaussianBlur(gray, (3, 3), 0)
    edged = cv2.Canny(blurred, 50, 150)

    # Contouren zoeken
    contours, _ = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    canvas = np.ones_like(image) * 255
    painted = clustered_image.copy()
    h, w = gray.shape
    label_map = labels.reshape(h, w)

    font = cv2.FONT_HERSHEY_SIMPLEX

    for cnt in contours:
        mask = np.zeros(gray.shape, dtype="uint8")
        cv2.drawContours(mask, [cnt], -1, 255, -1)
        masked_labels = label_map[mask == 255]
        if len(masked_labels) == 0:
            continue
        most_common_label = np.bincount(masked_labels).argmax()
        cv2.drawContours(canvas, [cnt], -1, (0, 0, 0), 1)

        # Nummer in vlak plaatsen
        M = cv2.moments(cnt)
        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            cv2.putText(canvas, str(most_common_label + 1), (cx, cy), font, 0.4, (0, 0, 0), 1)

    canvas_img = Image.fromarray(canvas)
    painted_img = Image.fromarray(painted)
    return canvas_img
