from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import os
import json
import shutil
from datetime import datetime

import torch
import torchvision.transforms as T
from PIL import Image
import numpy as np
import faiss

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------------------------
# PATHS
# --------------------------------------------------

IMAGE_DB     = "../HAL-IMS-MVC/wwwroot/imagedatabase"
DATASET_DIR  = "dataset_aug"
EMBEDDINGS_DIR = "embeddings"

# index.faiss + labels.npy
#   → built from dataset_aug/  (folder name = component label: bolt, pin, screw…)
#   → used by classify_component() during Assign to predict component type
INDEX_PATH   = os.path.join(EMBEDDINGS_DIR, "index.faiss")
LABELS_PATH  = os.path.join(EMBEDDINGS_DIR, "labels.npy")

# imgdb_index.faiss + imgdb_labels.npy
#   → built from imagedatabase/  (folder name = part number: ASD123, ASD234…)
#   → used by search_image() during Identify to match uploaded image to a part
IMGDB_INDEX_PATH  = os.path.join(EMBEDDINGS_DIR, "imgdb_index.faiss")
IMGDB_LABELS_PATH = os.path.join(EMBEDDINGS_DIR, "imgdb_labels.npy")

os.makedirs(IMAGE_DB, exist_ok=True)
os.makedirs(EMBEDDINGS_DIR, exist_ok=True)

# --------------------------------------------------
# MODEL
# --------------------------------------------------

print("Loading DINOv2 model...")
model = torch.hub.load("facebookresearch/dinov2", "dinov2_vits14")
model.eval()

transform = T.Compose([
    T.Resize((224, 224)),
    T.ToTensor(),
])

# --------------------------------------------------
# HELPERS
# --------------------------------------------------

def get_embedding(image_path: str) -> np.ndarray:
    image = Image.open(image_path).convert("RGB")
    tensor = transform(image).unsqueeze(0)

    with torch.no_grad():
        embedding = model(tensor)

    return embedding.squeeze().numpy().astype("float32")


def classify_component(embedding: np.ndarray) -> str:
    """
    Predict component type from index.faiss + labels.npy.
    These are built from dataset_aug/ where folder name = component label.
    Uses k-NN majority vote.
    """
    from collections import Counter

    if not os.path.exists(INDEX_PATH) or not os.path.exists(LABELS_PATH):
        print("classify_component: index.faiss or labels.npy not found.")
        return ""

    index  = faiss.read_index(INDEX_PATH)
    labels = np.load(LABELS_PATH, allow_pickle=True)

    emb = embedding.astype("float32")
    emb = emb / np.linalg.norm(emb)

    k = min(5, index.ntotal)
    D, I = index.search(np.array([emb]), k)

    neighbor_labels  = [str(labels[i]) for i in I[0]]
    final_prediction = Counter(neighbor_labels).most_common(1)[0][0]

    return final_prediction


def load_metadata(part_number: str) -> dict | None:
    part_dir      = os.path.join(IMAGE_DB, part_number)
    metadata_path = os.path.join(part_dir, "metadata.json")

    if not os.path.exists(metadata_path):
        return None

    with open(metadata_path, "r", encoding="utf-8") as f:
        return json.load(f)


# --------------------------------------------------
# BUILD IMGDB INDEX
# Scans imagedatabase/, embeds every image, label = part_number folder name
# Saves imgdb_index.faiss + imgdb_labels.npy
# --------------------------------------------------

def build_imgdb_index():
    """
    Build imgdb_index.faiss + imgdb_labels.npy from imagedatabase/.
    Each image is embedded with DINOv2 and labelled with its part number.
    Called on startup if missing, and after every add_part / rebuild_index.
    """
    print("Building imgdb_index.faiss from imagedatabase...")

    features = []
    labels   = []

    for part_number in os.listdir(IMAGE_DB):
        part_dir = os.path.join(IMAGE_DB, part_number)

        if not os.path.isdir(part_dir):
            continue

        for file_name in os.listdir(part_dir):
            if not file_name.lower().endswith((".jpg", ".jpeg", ".png", ".bmp", ".webp")):
                continue

            image_path = os.path.join(part_dir, file_name)

            try:
                emb = get_embedding(image_path)
                emb = emb / np.linalg.norm(emb)   # normalize for cosine similarity
                features.append(emb)
                labels.append(part_number)
            except Exception as e:
                print(f"Skipped {image_path}: {e}")

    if not features:
        print("No images found in imagedatabase — imgdb index not built.")
        return

    features  = np.array(features).astype("float32")
    dimension = features.shape[1]

    index = faiss.IndexFlatIP(dimension)
    index.add(features)

    faiss.write_index(index, IMGDB_INDEX_PATH)
    np.save(IMGDB_LABELS_PATH, np.array(labels))

    print(f"imgdb_index.faiss built: {len(labels)} images, dim={dimension}")


# Always rebuild imgdb index on startup so it stays in sync with imagedatabase
build_imgdb_index()

# --------------------------------------------------
# REBUILD INDEX  (dataset_aug → index.faiss + labels.npy)
# --------------------------------------------------

@app.get("/rebuild_index")
def rebuild_index():
    """
    Rebuild index.faiss + labels.npy from dataset_aug/.
    Folder name = component label (bolt, pin, screw, etc.)
    Also rebuilds imgdb_index.faiss so both stay in sync.
    """
    features = []
    labels   = []

    if not os.path.exists(DATASET_DIR):
        return {
            "message": f"dataset_aug folder not found at '{DATASET_DIR}'.",
            "total_images": 0
        }

    for component_name in os.listdir(DATASET_DIR):
        component_dir = os.path.join(DATASET_DIR, component_name)

        if not os.path.isdir(component_dir):
            continue

        for file_name in os.listdir(component_dir):
            if not file_name.lower().endswith((".jpg", ".jpeg", ".png", ".bmp", ".webp")):
                continue

            image_path = os.path.join(component_dir, file_name)

            try:
                emb = get_embedding(image_path)
                emb = emb / np.linalg.norm(emb)   # normalize for cosine similarity
                features.append(emb)
                labels.append(component_name)
            except Exception as e:
                print(f"Skipped {image_path}: {e}")

    if not features:
        return {"message": "No images found in dataset_aug.", "total_images": 0}

    features  = np.array(features).astype("float32")
    dimension = features.shape[1]

    index = faiss.IndexFlatIP(dimension)
    index.add(features)

    faiss.write_index(index, INDEX_PATH)
    np.save(LABELS_PATH, np.array(labels))

    # Also rebuild imgdb index
    build_imgdb_index()

    return {
        "message": "index.faiss (dataset_aug) and imgdb_index.faiss (imagedatabase) rebuilt successfully.",
        "dataset_images": len(labels)
    }


# --------------------------------------------------
# ADD PART
# --------------------------------------------------

@app.post("/add_part")
async def add_part(
    part_number: str = Form(...),
    description: str = Form(""),
    files: list[UploadFile] = File(...)
):
    part_number = part_number.strip()

    part_dir = os.path.join(IMAGE_DB, part_number)
    os.makedirs(part_dir, exist_ok=True)

    saved_images      = []
    predicted_component = ""

    for file in files:
        filename  = os.path.basename(file.filename)
        img_path  = os.path.join(part_dir, filename)

        with open(img_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        saved_images.append(filename)

        # Classify component type using dataset index (index.faiss + labels.npy)
        try:
            embedding           = get_embedding(img_path)
            predicted_component = classify_component(embedding)
        except Exception as e:
            print("Component classification failed:", e)

    metadata = {
        "part_number":    part_number,
        "component_name": predicted_component,
        "description":    description,
        "images":         saved_images,
        "created_at":     str(datetime.now())
    }

    with open(os.path.join(part_dir, "metadata.json"), "w") as f:
        json.dump(metadata, f, indent=4)

    # Rebuild imgdb index so the new part is searchable immediately in Identify
    build_imgdb_index()

    return {
        "status":         "success",
        "component_name": predicted_component
    }


# --------------------------------------------------
# SEARCH BY PART NUMBER
# --------------------------------------------------

@app.post("/search/part")
def search_part(part_number: str = Form(...)):
    part_number = part_number.strip()
    data        = load_metadata(part_number)

    if not data:
        return {
            "results": [],
            "message": "Part not found. Please assign it first."
        }

    return {
        "results": [
            {
                "rank":           1,
                "part_label":     data.get("part_number", part_number),
                "component_name": data.get("component_name", ""),
                "description":    data.get("description", ""),
                "confidence_pct": 100.0,
                "images":         data.get("images", []),
                "verdict":        "HIGH"
            }
        ]
    }


# --------------------------------------------------
# SEARCH BY IMAGE
# Uses imgdb_index.faiss + imgdb_labels.npy
# Labels = part numbers (ASD123, ASD234…)
# Returns full part metadata + images for the best match
# --------------------------------------------------

@app.post("/search/image")
async def search_image(file: UploadFile = File(...)):

    query_path = "query.jpg"
    print(f"Received file: {file.filename}")

    with open(query_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    emb = get_embedding(query_path)
    emb = emb.astype("float32")
    emb = emb / np.linalg.norm(emb)   # normalize for cosine similarity

    if not os.path.exists(IMGDB_INDEX_PATH) or not os.path.exists(IMGDB_LABELS_PATH):
        return {
            "results": [],
            "message": "Image database index not found. Please add parts first via Assign."
        }

    imgdb_index  = faiss.read_index(IMGDB_INDEX_PATH)
    imgdb_labels = np.load(IMGDB_LABELS_PATH, allow_pickle=True)

    if imgdb_index.ntotal == 0:
        return {
            "results": [],
            "message": "Image database index is empty. Please add parts first via Assign."
        }

    D, I = imgdb_index.search(np.array([emb]), k=1)

    similarity  = float(D[0][0])                        # cosine similarity (0–1)
    part_number = str(imgdb_labels[I[0][0]])
    confidence  = round(max(0.0, similarity * 100), 2)

    print(f"Best match: {part_number}, similarity={similarity:.4f}, confidence={confidence}%")

    data = load_metadata(part_number)

    if data is None:
        return {
            "results": [],
            "message": f"Matched part '{part_number}' but metadata.json not found."
        }

    return {
        "results": [
            {
                "rank":           1,
                "part_label":     data["part_number"],
                "component_name": data.get("component_name", ""),
                "description":    data.get("description", ""),
                "confidence_pct": confidence,
                "images":         data.get("images", []),
                "verdict": (
                    "HIGH"   if confidence >= 90
                    else "MEDIUM" if confidence >= 70
                    else "LOW"
                )
            }
        ]
    }


# --------------------------------------------------
# PARTS REGISTRY
# --------------------------------------------------

@app.get("/parts")
def get_parts():

    parts = []

    for part in os.listdir(IMAGE_DB):
        part_dir = os.path.join(IMAGE_DB, part)

        if not os.path.isdir(part_dir):
            continue

        meta_file = os.path.join(part_dir, "metadata.json")

        component   = ""
        description = ""
        images      = []

        if os.path.exists(meta_file):
            with open(meta_file) as f:
                data = json.load(f)

            component   = data.get("component_name", "")
            description = data.get("description", "")
            images      = data.get("images", [])

        parts.append({
            "part_number":    part,
            "component_name": component,
            "description":    description,
            "image_count":    len(images)
        })

    return {
        "total_parts": len(parts),
        "parts":       parts
    }