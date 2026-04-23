import cv2
import os
import json
import subprocess
from datetime import datetime

database_dir = "database"
query_dir = "query"

os.makedirs(query_dir, exist_ok=True)

# create unique query image name
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
query_image_name = f"query_{timestamp}.jpg"
query_image_path = os.path.join(query_dir, query_image_name)

cap = cv2.VideoCapture(0)

print("Press 'c' to capture image")

while True:

    ret, frame = cap.read()

    if not ret:
        break

    cv2.imshow("Camera", frame)

    key = cv2.waitKey(1) & 0xFF

    if key == ord('c'):
        cv2.imwrite(query_image_path, frame)
        print("Query image saved:", query_image_path)
        break

cap.release()
cv2.destroyAllWindows()

# run AI recognition
result = subprocess.check_output(
    ["python", "search.py", query_image_path]
).decode()

detected_object = result.split(":")[-1].strip()

print("Detected object:", detected_object)

# search database
for part in os.listdir(database_dir):

    json_path = os.path.join(database_dir, part, "metadata.json")

    if not os.path.exists(json_path):
        continue

    with open(json_path) as f:
        data = json.load(f)

    if detected_object in data["detected_objects"]:

        print("\nMatch Found")
        print("Part Number:", data["part_number"])
        print("Description:", data["description"])

        for img in data["images"]:

            img_path = os.path.join(database_dir, part, img)

            image = cv2.imread(img_path)

            cv2.imshow(img, image)
            cv2.waitKey(0)

        cv2.destroyAllWindows()
        break