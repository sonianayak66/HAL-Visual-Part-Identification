import torch
import torchvision.transforms as T
from PIL import Image
import os
import numpy as np
import faiss

print("Loading DINOv2 model once...")

model = torch.hub.load('facebookresearch/dinov2', 'dinov2_vits14')
model.eval()

print("Model ready")

transform = T.Compose([
    T.Resize((224,224)),
    T.ToTensor(),
])

dataset_path = "dataset_aug"

features = []
labels = []

print("Processing dataset:", dataset_path)

for label in os.listdir(dataset_path):

    class_path = os.path.join(dataset_path, label)

    if not os.path.isdir(class_path):
        continue

    for img_name in os.listdir(class_path):

        if not img_name.lower().endswith((".jpg",".jpeg",".png",".bmp",".webp")):
            continue

        img_path = os.path.join(class_path, img_name)

        try:

            image = Image.open(img_path).convert("RGB")

            tensor = transform(image).unsqueeze(0)

            with torch.no_grad():
                embedding = model(tensor)

            embedding = embedding.squeeze().numpy().astype("float32")

            features.append(embedding)
            labels.append(str(label))   # ensure plain string

        except Exception as e:
            print("Skipped:", img_path, e)

features = np.array(features).astype("float32")

if len(features) == 0:
    print("No images found. Index not created.")
    exit()

# normalize all embeddings for cosine similarity
faiss.normalize_L2(features)

os.makedirs("embeddings", exist_ok=True)

dimension = features.shape[1]

index = faiss.IndexFlatIP(dimension)

index.add(features)

faiss.write_index(index, "embeddings/index.faiss")

np.save("embeddings/labels.npy", np.array(labels))

print("Index built successfully")
print("Total images indexed:", len(labels))