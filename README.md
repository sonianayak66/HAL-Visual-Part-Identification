# HAL Visual Part Identification System

A full-stack aerospace **Inventory Management System (IMS)** for Hindustan Aeronautics Limited (HAL) that identifies mechanical components from an uploaded image, a live webcam capture, or a part-number lookup — powered by a **DINOv2 Vision Transformer** and **FAISS** vector similarity search.

---

## Architecture

```
┌──────────────────┐   HTTP/multipart   ┌───────────────────┐   DINOv2 + FAISS   ┌─────────────┐
│  Browser (HTML5) │ ─────────────────▶ │  ASP.NET Core 8   │ ─────────────────▶ │  FastAPI    │
│  Razor + JS      │ ◀───────────────── │  MVC (C#)         │ ◀───────────────── │  (Python)   │
└──────────────────┘                    └───────────────────┘                    └─────────────┘
                                              Port 5000+                            Port 8000
```

Two cooperating services:

| Component      | Stack                                              | Role                                         |
| -------------- | -------------------------------------------------- | -------------------------------------------- |
| `HAL-IMS-MVC/` | ASP.NET Core 8.0, C#, Razor, vanilla JS            | Web UI, controllers, HTTP bridge             |
| `haltemp/`     | FastAPI, PyTorch, DINOv2, FAISS, OpenCV, Pillow    | ML service: embeddings + similarity search   |

---

## Features

- **Identify** — upload an image, capture from webcam, or search by part number; returns ranked matches with confidence % (HIGH ≥ 90, MEDIUM ≥ 70, LOW < 70).
- **Assign** — register a new part with multiple images; component type (bolt, pin, bearing, etc.) is auto-classified via k-NN majority vote.
- **Parts Registry** — browse all indexed parts; trigger a full index rebuild on demand.
- **Webcam capture** — HTML5 MediaDevices + Canvas; no browser plugins.
- **Dual FAISS index** — one for component-type classification, one for part-number retrieval.
- **Data augmentation** — `dataaug.py` generates rotated / lighting-varied samples to improve robustness.

---

## Tech Stack

**Backend (Web)** — ASP.NET Core 8.0, C#, dependency injection, async controllers, multipart form-data
**Backend (ML)** — FastAPI, PyTorch, `torchvision.transforms`, FAISS (`IndexFlatIP`), OpenCV, Pillow
**Model** — DINOv2 Vision Transformer (`dinov2_vits14`) → 384-dim L2-normalised embeddings
**Frontend** — Razor Views, HTML5, vanilla JavaScript, MediaDevices API, Canvas
**Data** — JSON metadata per part; numpy-serialised labels; FAISS binary indices

---

## Project Structure

```
HAL Final/
├── HAL-IMS-MVC/                   # ASP.NET Core MVC web app
│   ├── Controllers/               # IdentifyController, AssignController, PartsController
│   ├── Models/                    # ViewModels + result DTOs
│   ├── Services/                  # HalApiService (HTTP bridge to FastAPI)
│   ├── Views/                     # Razor pages (Identify, Assign, Parts, Shared)
│   ├── wwwroot/
│   │   └── imagedatabase/         # Registered part images (organised by part number)
│   ├── Program.cs
│   ├── appsettings.json
│   └── HAL-IMS-MVC.csproj
│
└── haltemp/                       # Python ML service
    ├── api_server.py              # FastAPI app (entry point)
    ├── build_index.py             # Build FAISS indices from datasets
    ├── search.py                  # Component-type classification
    ├── search_by_image.py         # Part-number retrieval by image
    ├── search_by_part.py          # Part-number metadata lookup
    ├── camera_search.py           # Webcam-based querying
    ├── dataaug.py                 # Data augmentation (rotation + lighting)
    ├── dataset_aug/               # Augmented training images (per component)
    ├── embeddings/                # FAISS indices + label arrays
    └── requirements.txt
```

---

## Setup

### Prerequisites

- .NET 8.0 SDK
- Python 3.10+
- ~2 GB disk (DINOv2 weights are downloaded on first run via `torch.hub`)

### 1. Start the Python ML service

```bash
cd haltemp
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python api_server.py            # serves on http://127.0.0.1:8000
```

### 2. Start the ASP.NET Core app

```bash
cd HAL-IMS-MVC
dotnet restore
dotnet run                       # serves on http://localhost:5xxx (see console)
```

Open the URL printed by `dotnet run` in a browser.

### 3. (Optional) Rebuild indices

Hit `GET /rebuild_index` on the FastAPI service, or use the **Parts → Rebuild Index** button in the UI.

---

## REST API (FastAPI)

| Endpoint         | Method | Purpose                                                      |
| ---------------- | ------ | ------------------------------------------------------------ |
| `/add_part`      | POST   | Register new part; auto-classify component; rebuild index    |
| `/search/image`  | POST   | Upload query image → return best-matching part + confidence  |
| `/search/part`   | POST   | Part-number lookup → return metadata JSON                    |
| `/rebuild_index` | GET    | Rebuild both FAISS indices from current data                 |
| `/parts`         | GET    | List all registered parts                                    |

---

## Demo

A full walkthrough of the system — identify, assign, and part-lookup flows.

<video src="https://github.com/sonianayak66/HAL-Visual-Part-Identification/releases/download/v1.0/demo.mp4" controls width="100%"></video>

https://github.com/sonianayak66/HAL-Visual-Part-Identification/releases/download/v1.0/demo.mp4

> If the player above does not render, [click here to watch](https://github.com/sonianayak66/HAL-Visual-Part-Identification/releases/download/v1.0/demo.mp4).

<details>
<summary>What the demo shows</summary>

- Registering a new part (Assign module) with multiple images
- Auto-classification of component type via k-NN majority vote
- Identifying a part by uploading an image
- Identifying a part via live webcam capture
- Part-number lookup returning full metadata
- Confidence scoring (HIGH / MEDIUM / LOW verdicts)

</details>

---

## Notes

- Only L2-normalised embeddings are stored — `IndexFlatIP` treats inner product as cosine similarity.
- On first launch, PyTorch downloads DINOv2 weights (~90 MB) to the torch hub cache.
- `appsettings.json → HalApi:BaseUrl` controls the FastAPI endpoint used by the MVC app (default `http://127.0.0.1:8000/`).

---

## License

Academic / portfolio project.
