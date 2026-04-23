import numpy as np
print(np.unique(np.load("embeddings/labels.npy")))

import numpy as np
labels = np.load("embeddings/labels.npy")
print("Total embeddings:", len(labels))