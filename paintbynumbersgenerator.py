
import cv2
import numpy as np
from sklearn.cluster import KMeans
from PIL import Image

def generate_paint_by_numbers(pil_image, num_colors):
    image = np.array(pil_image)

    # Kleurreductie via KMeans
    pixels = image.reshape(-1, 3)
    kmeans = KMeans(n_clusters=num_colors, random_state=42).fit(pixels)
    labels = kmeans.labels_
    clustered = kmeans.cluster_centers_.astype("uint8")[labels]
    clustered_image = clustered.reshape(image.shape)

    # Grijs en randdetectie
    gray = cv2.cvtColor(clustered_image, cv2.COLOR_RGB2GRAY)
    blurred = cv2.medianBlur(gray, 5)
    edged = cv2.Canny(blurred, 30, 100)

    # Contouren vinden
    contours, _ = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    result = np.ones_like(image) * 255
    h, w = gray.shape
    label_map = labels.reshape(h, w)

    font = cv2.FONT_HERSHEY_SIMPLEX

    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < 150:
            continue
        mask = np.zeros(gray.shape, dtype="uint8")
        cv2.drawContours(mask, [cnt], -1, 255, -1)
        masked_labels = label_map[mask == 255]
        if len(masked_labels) == 0:
            continue
        most_common_label = np.bincount(masked_labels).argmax()
        color = kmeans.cluster_centers_[most_common_label].astype("uint8").tolist()
        cv2.drawContours(result, [cnt], -1, color, -1)
        cv2.drawContours(result, [cnt], -1, (0, 0, 0), 1)

        M = cv2.moments(cnt)
        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            cv2.putText(result, str(most_common_label + 1), (cx - 5, cy + 5), font, 0.5, (0, 0, 0), 1, cv2.LINE_AA)

    final_image = Image.fromarray(result)
    return final_image
