import json
import numpy as np
from transformers import AutoTokenizer, AutoModel
import torch
import pickle
import os
from pathlib import Path
from tqdm import tqdm

# Input and output paths
VECTOR_JSON_PATH = "scrape/data/all_weekly_rankings_vectors.json"
EMBEDDINGS_PATH = "data/fantasy_embeddings.npy"
METADATA_PATH = "data/fantasy_metadata.pkl"

def get_embeddings(texts, model, tokenizer):
    embeddings = []
    for text in tqdm(texts, desc="Creating embeddings"):
        inputs = tokenizer(text, padding=True, truncation=True, return_tensors="pt")
        with torch.no_grad():
            outputs = model(**inputs)
            embedding = outputs.last_hidden_state.mean(dim=1).numpy()[0]
            embeddings.append(embedding)
    return np.array(embeddings)

# Load vector data
with open(VECTOR_JSON_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)

# Extract metadata and text for encoding
texts = [item["text"] for item in data]
metadata = [item["metadata"] for item in data]

# Initialize model and tokenizer
model_name = 'sentence-transformers/all-MiniLM-L6-v2'
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)

# Create embeddings
embeddings = get_embeddings(texts, model, tokenizer)

# Save embeddings and metadata
os.makedirs("data", exist_ok=True)
np.save(EMBEDDINGS_PATH, embeddings)

with open(METADATA_PATH, "wb") as f:
    pickle.dump(metadata, f)

print(f"✅ Saved embeddings to: {EMBEDDINGS_PATH}")
print(f"✅ Saved metadata to: {METADATA_PATH}")
