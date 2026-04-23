import os
import json
import subprocess
import shutil
from datetime import datetime
import sys

database_dir = "../HAL-IMS-MVC/wwwroot/imagedatabase"

part_number = sys.argv[1]
description = sys.argv[2]
image_paths = sys.argv[3:]

part_dir = os.path.join(database_dir, part_number)
os.makedirs(part_dir, exist_ok=True)

img_count = len([f for f in os.listdir(part_dir) if f.endswith(".jpg")])

detected_objects = []

for img in image_paths:

    img_count += 1
    img_name = f"img_{img_count}.jpg"
    img_path = os.path.join(part_dir, img_name)

    shutil.copy(img, img_path)

    print("Saved:", img_path)

    # Run AI recognition
    result = subprocess.check_output(
        ["python", "search.py", img]
    ).decode()

    try:
        data = json.loads(result)
        detected_object = data["component"]
    except:
        detected_object = "unknown"

    detected_objects.append(detected_object)

    print("Detected:", detected_object)


metadata = {
    "part_number": part_number,
    "description": description,
    "component_name": detected_objects[0] if detected_objects else "unknown",
    "images": [f for f in os.listdir(part_dir) if f.endswith(".jpg")],
    "created_at": str(datetime.now())
}

json_path = os.path.join(part_dir, "metadata.json")

with open(json_path, "w") as f:
    json.dump(metadata, f, indent=4)

print("Metadata saved.")

subprocess.run(["python", "build_index.py"])