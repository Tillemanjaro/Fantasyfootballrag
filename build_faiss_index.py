import json
import numpy as np
import faiss
import pickle
import os

# Input and output paths
VECTOR_JSON_PATH = "scrape/data/all_weekly_rankings_vectors.json"  # adjust if needed
FAISS_INDEX_PATH = "data/fantasy_index.faiss"
METADATA_PATH = "data/fantasy_metadata.pkl"

# Load vector data
with open(VECTOR_JSON_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

# Extract vectors and metadata
vectors = np.array([item["vector"] for item in data]).astype("float32")
metadata = [item["metadata"] for item in data]

# Normalize vectors for cosine similarity
faiss.normalize_L2(vectors)

# Create and populate FAISS index
dim = vectors.shape[1]
index = faiss.IndexFlatIP(dim)
index.add(vectors)

# Save the index
os.makedirs("data", exist_ok=True)
faiss.write_index(index, FAISS_INDEX_PATH)

# Save metadata
with open(METADATA_PATH, "wb") as f:
    pickle.dump(metadata, f)

print(f"✅ Saved FAISS index to: {FAISS_INDEX_PATH}")
print(f"✅ Saved metadata to: {METADATA_PATH}")
