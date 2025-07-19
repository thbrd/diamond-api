
import cv2
import numpy as np
from sklearn.cluster import KMeans
from PIL import Image

def generate_paint_by_numbers(pil_image, num_colors):
    image = np.array(pil_image)
    h, w = image.shape[:2]

    # Kleurreductie met KMeans
    pixels = image.reshape(-1, 3)
    kmeans = KMeans(n_clusters=num_colors, random_state=42).fit(pixels)
    labels = kmeans.labels_
    clustered = kmeans.cluster_centers_.astype("uint8")[labels].reshape(image.shape)

    # Grijs + contouren
    gray = cv2.cvtColor(clustered, cv2.COLOR_RGB2GRAY)
    blurred = cv2.GaussianBlur(gray, (3, 3), 0)
    edged = cv2.Canny(blurred, 50, 150)
    contours, _ = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Nummering en tekenen
    label_map = labels.reshape(h, w)
    font = cv2.FONT_HERSHEY_SIMPLEX
    output = clustered.copy()

    for cnt in contours:
        mask = np.zeros((h, w), dtype="uint8")
        cv2.drawContours(mask, [cnt], -1, 255, -1)
        M = cv2.moments(cnt)
        if M["m00"] != 0:
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            label = label_map[cY, cX]
            cv2.putText(output, str(label), (cX - 5, cY + 5), font, 0.4, (0, 0, 0), 1)

    # Trek contouren
    cv2.drawContours(output, contours, -1, (0, 0, 0), 1)

    return Image.fromarray(output)
