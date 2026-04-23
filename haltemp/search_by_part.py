import os
import cv2
import json

database_dir = "database"

part_number = input("Enter part number: ").strip()

part_dir = os.path.join(database_dir, part_number)

if not os.path.exists(part_dir):
    print("Part not found.")
    exit()

json_file = os.path.join(part_dir, "metadata.json")

with open(json_file) as f:
    metadata = json.load(f)

print("\nPart Number:", metadata["part_number"])
print("Description:", metadata["description"])
print("Detected Object:", metadata["detected_objects"])

for img in metadata["images"]:

    img_path = os.path.join(part_dir, img)

    image = cv2.imread(img_path)

    cv2.imshow(img, image)
    cv2.waitKey(0)

cv2.destroyAllWindows()