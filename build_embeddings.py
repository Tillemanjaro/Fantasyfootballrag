import json
import numpy as np
from sentence_transformers import SentenceTransformer
import pickle
import os
from pathlib import Path

# Input and output paths
VECTOR_JSON_PATH = "scrape/data/all_weekly_rankings_vectors.json"  # adjust if needed
EMBEDDINGS_PATH = "data/fantasy_embeddings.npy"
METADATA_PATH = "data/fantasy_metadata.pkl"

# Load vector data
with open(VECTOR_JSON_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

# Extract metadata and text for encoding
texts = [item["text"] for item in data]  # Assuming each item has a "text" field
metadata = [item["metadata"] for item in data]

# Initialize the model and create embeddings
model = SentenceTransformer('all-MiniLM-L6-v2')
embeddings = model.encode(texts, show_progress_bar=True)

# Save embeddings and metadata
os.makedirs("data", exist_ok=True)
np.save(EMBEDDINGS_PATH, embeddings)

# Save metadata
with open(METADATA_PATH, "wb") as f:
    pickle.dump(metadata, f)

print(f"✅ Saved embeddings to: {EMBEDDINGS_PATH}")
print(f"✅ Saved metadata to: {METADATA_PATH}")
