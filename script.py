import cv2
import numpy as np
import os

#input_folder = "versuch1-test"
#output_folder = "test1"
input_folder = "Dias/tray 8"
output_folder = "Dias/tray 8 cropped"
os.makedirs(output_folder, exist_ok=True)

config = {
    "primary_threshold": 100,
    "secondary_threshold": 100,
    "threshold_change": 1.5,
}

def find_monotonic_borders(image, max_offset):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    height, width = gray.shape

    # Analyze horizontal and vertical pixel intensity profiles
    max_h_offset = int(height * max_offset)
    max_w_offset = int(width * max_offset)

    # Variance along rows and columns
    row_variance = np.var(gray, axis=1)
    col_variance = np.var(gray, axis=0)

    # print 100 most right values of col_variance
    # top
 #   print(col_variance[:200])
    # left
#    print(row_variance[:200])

    def detect_border(variance, max_offset, primary_threshold, secondary_threshold, change_threshold):
        if variance[0] > primary_threshold:
 #           print(f"Detected border at 0 because of primary threshold")
            return 0
        for i in range(max_offset):
            if variance[i] > secondary_threshold:
     #           print(f"Detected border at {i} because of secondary threshold")
                return i
        for i in range(max_offset, len(variance) - max_offset):
            left_avg = np.mean(variance[i-10:i])
            right_avg = np.mean(variance[i+1:i+11])
            if variance[i] > secondary_threshold or (right_avg > max(left_avg, 30) * change_threshold):  # 20 is a chosen magic number to avoid false positives (eg 2 is bigger than 1.5*1 but not a border)
  #              print(f"Detected border at {i}")
  #              print(f"Left avg: {left_avg}, right avg: {right_avg}")
                return i
        return 0

#    print("Top border")
    top = detect_border(row_variance, max_h_offset, config["primary_threshold"], config["secondary_threshold"], config["threshold_change"])
 #   print("Bottom border")
    bottom = detect_border(row_variance[::-1], max_h_offset, config["primary_threshold"], config["secondary_threshold"], config["threshold_change"])
    bottom = height - bottom

    left = detect_border(col_variance, max_w_offset, config["primary_threshold"], config["secondary_threshold"], config["threshold_change"])
    right = detect_border(col_variance[::-1], max_w_offset, config["primary_threshold"], config["secondary_threshold"], config["threshold_change"])
    right = width - right

    return {"top": top, "bottom": bottom, "left": left, "right": right}

def find_monotonic_borders_fallback(image, max_offset, crop_percent):
    h, w = image.shape[:2]
    cropped_image = image[int(h * crop_percent): int(h * (1 - crop_percent)), int(w * crop_percent): int(w * (1 - crop_percent))]
    
    # Get the borders from the cropped image
    cropped_borders = find_monotonic_borders(cropped_image, max_offset)

    # Rescale the cropped borders back to the full-size image
    top_rescaled = int(cropped_borders["top"] / (1 - crop_percent))
    bottom_rescaled = int(cropped_borders["bottom"] / (1 -2* crop_percent))
    left_rescaled = int(cropped_borders["left"] / (1 - crop_percent))
    right_rescaled = int(cropped_borders["right"] / (1 -2* crop_percent))

    # Adjust the borders to crop further outside (add some padding to prevent cutting too close)
    return {
        "top": max(top_rescaled - 1, 0),  # Ensure no negative index
        "bottom": min(bottom_rescaled + 1, image.shape[0]),
        "left": max(left_rescaled - 1, 0),  # Ensure no negative index
        "right": min(right_rescaled + 1, image.shape[1])
    }

def crop_image(image, borders):
    top, bottom, left, right = borders["top"], borders["bottom"], borders["left"], borders["right"]
    return image[top:bottom, left:right]

def process_image(image, max_offset=0.25, crop_percent=0.015, fallback_threshold=0.005):
    height, width = image.shape[:2]
    borders = find_monotonic_borders(image, max_offset)
    fallback_borders = find_monotonic_borders_fallback(image, max_offset, crop_percent)
    print(f"borders: {borders}")
    print(f"fallback_borders: {fallback_borders}")
    
    # For each border, check if the detected crop is too small (less than 0.5% of image size)
    if abs(borders["top"]) < fallback_threshold * height:
        if fallback_borders["top"] > borders["top"]:
            borders["top"] = fallback_borders["top"]
            print("Using fallback for top border")

    if abs(borders["bottom"] - height) < fallback_threshold * height:
        if fallback_borders["bottom"] < borders["bottom"]:
            borders["bottom"] = fallback_borders["bottom"]
            print(f"Using fallback for bottom border")

    if abs(borders["left"]) < fallback_threshold * width:
        if fallback_borders["left"] > borders["left"]:
            borders["left"] = fallback_borders["left"]
            print(f"Using fallback for left border")

    if abs(borders["right"] - width) < fallback_threshold * width:
        if fallback_borders["right"] < borders["right"]:
            borders["right"] = fallback_borders["right"]
            print(f"Using fallback for right border")

    return crop_image(image, borders)

# Process all images in the input folder
for filename in os.listdir(input_folder):
    if filename.endswith(".jpg"):
        print(f"  --  Processing {filename}")
        filepath = os.path.join(input_folder, filename)
        image = cv2.imread(filepath)
        cropped = process_image(image)
        output_path = os.path.join(output_folder, filename)
        cv2.imwrite(output_path, cropped, [int(cv2.IMWRITE_JPEG_OPTIMIZE ), 1])
