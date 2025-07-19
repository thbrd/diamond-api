
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from sklearn.cluster import KMeans

def generate_paint_by_numbers(image_path, n_colors=24):
    image = Image.open(image_path).convert("RGB")
    image = image.resize((300, 300))

    data = np.array(image).reshape(-1, 3)
    kmeans = KMeans(n_clusters=n_colors, n_init="auto").fit(data)
    labels = kmeans.predict(data)
    clustered = kmeans.cluster_centers_[labels].reshape(image.size[1], image.size[0], 3).astype(np.uint8)

    # Create painted image
    painted = Image.fromarray(clustered)

    # Create canvas image with numbers
    canvas = Image.new("RGB", image.size, "white")
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.load_default()

    label_matrix = labels.reshape(image.size[1], image.size[0])
    cell_size = 10
    for y in range(0, image.size[1], cell_size):
        for x in range(0, image.size[0], cell_size):
            crop = label_matrix[y:y+cell_size, x:x+cell_size]
            most_common = np.bincount(crop.flatten()).argmax()
            draw.rectangle([x, y, x+cell_size, y+cell_size], outline="black")
            draw.text((x + 2, y + 1), str(int(most_common)+1), fill="black", font=font)

    return painted, canvas
