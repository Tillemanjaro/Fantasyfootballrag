import json
import os
import openai
import time
from tqdm import tqdm

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Set OpenAI API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

# File paths
json_path = os.path.join(os.path.dirname(__file__), "..", "scrape", "data", "all_weekly_rankings.json")
output_path = os.path.join(os.path.dirname(__file__), "..", "scrape", "data", "all_weekly_rankings_vectors.json")

# Load the data
with open(json_path, "r", encoding="utf-8") as f:
    data = json.load(f)

# Function to build the input text for vectorization
def build_embedding_text(item):
    return (
        f"{item['player_name']} ({item['player_positions']} - {item['player_team_id']}) is ranked #{item['rank_ecr']} "
        f"against {item['player_opponent']}. Start/sit grade: {item.get('start_sit_grade', 'N/A')}. "
        f"Ownership: {item.get('player_owned_avg', 'N/A')}%. "
        f"Rank range: {item.get('rank_min')} to {item.get('rank_max')} (avg: {item.get('rank_ave')}). "
        f"{item.get('note', '')} {item.get('recommendation', '')}".strip()
    )

# Build list of texts and associated metadata
texts_with_meta = []
for item in data:
    try:
        text = build_embedding_text(item)
        if text:
            texts_with_meta.append((text, item))
    except Exception as e:
        print(f"Error processing item {item.get('player_name')}: {e}")

# Vectorize using OpenAI Embeddings API
vectors = []
for text, item in tqdm(texts_with_meta, desc="Vectorizing"):
    success = False
    while not success:
        try:
            response = openai.embeddings.create(
                input=text,
                model="text-embedding-ada-002"  # or "text-embedding-3-large" if available
            )
            success = True
        except openai.error.RateLimitError:
            time.sleep(1)
        except Exception as e:
            print(f"Embedding failed for {item['player_name']}: {e}")
            break

    if success:
        vectors.append({
            "text": text,
            "vector": response.data[0].embedding,
            "metadata": {
                "player_id": item["player_id"],
                "player_name": item["player_name"],
                "position": item["player_positions"],
                "team": item["player_team_id"],
                "opponent": item["player_opponent"],
                "ecr_rank": item["rank_ecr"],
                "start_sit_grade": item.get("start_sit_grade"),
                "pos_rank": item.get("pos_rank"),
            }
        })

# Save vectors to file
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(vectors, f, indent=2)

print(f"✅ Saved {len(vectors)} vectors to {output_path}")
