import torch
import torchvision.transforms as T
from PIL import Image
import numpy as np
import faiss
import sys
from collections import Counter
import json

model = torch.hub.load('facebookresearch/dinov2', 'dinov2_vits14')
model.eval()

transform = T.Compose([
    T.Resize((224, 224)),
    T.ToTensor(),
])

# load index
index = faiss.read_index("embeddings/index.faiss")
labels = np.load("embeddings/labels.npy")

query_image = sys.argv[1]

image = Image.open(query_image).convert("RGB")
tensor = transform(image).unsqueeze(0)

with torch.no_grad():
    embedding = model(tensor)

embedding = embedding.squeeze().numpy().astype("float32")

# normalize query embedding
embedding = embedding / np.linalg.norm(embedding)

k = 5
D, I = index.search(np.array([embedding]), k)

neighbor_labels = [str(labels[idx]) for idx in I[0]]

final_prediction = Counter(neighbor_labels).most_common(1)[0][0]

print(json.dumps({"component": final_prediction}))