def generate_paint_by_numbers(image, num_colors):
    # Resize image for processing
    image = image.resize((512, 512))
    img_array = np.array(image)
    img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
    Z = img_array.reshape((-1, 3))
    Z = np.float32(Z)
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    _, labels, centers = cv2.kmeans(Z, num_colors, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
    centers = np.uint8(centers)
    quantized = centers[labels.flatten()]
    quantized_image = quantized.reshape((img_array.shape))
    label_image = labels.flatten().reshape((img_array.shape[0], img_array.shape[1]))
    contour_img = np.ones_like(quantized_image, dtype=np.uint8) * 255
    font = cv2.FONT_HERSHEY_SIMPLEX
    scale_multiplier = 3
    font_scale = 0.4 * scale_multiplier
    line_thickness = int(1 * scale_multiplier)
    for label_val in range(num_colors):
        mask = np.uint8(label_image == label_val) * 255
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in contours:
            M = cv2.moments(cnt)
            if M['m00'] != 0:
                cX = int(M['m10'] / M['m00'])
                cY = int(M['m01'] / M['m00'])
                cv2.putText(contour_img, str(label_val + 1), (cX - 5 * scale_multiplier, cY + 5 * scale_multiplier), font, font_scale, (0, 0, 0), line_thickness, cv2.LINE_AA)
            cv2.drawContours(contour_img, [cnt], -1, (0, 0, 0), line_thickness, cv2.LINE_AA)
    contour_img = cv2.cvtColor(contour_img, cv2.COLOR_BGR2RGB)
    upscaled = cv2.resize(contour_img, (contour_img.shape[1]*scale_multiplier, contour_img.shape[0]*scale_multiplier), interpolation=cv2.INTER_NEAREST)
    return Image.fromarray(upscaled)
