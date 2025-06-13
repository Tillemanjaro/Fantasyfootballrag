import json
import os
import openai
import time
from tqdm import tqdm
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

# Set your OpenAI API key from environment variable
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("❌ OPENAI_API_KEY not found in environment variables or .env file")

print("🔑 Testing API key...")
try:
    # Test the API key with a simple embedding
    openai.api_key = api_key
    test_response = openai.embeddings.create(
        input="test",
        model="text-embedding-ada-002"
    )
    print("✅ API key is valid!")
except openai.AuthenticationError as e:
    print("❌ Authentication Error: Your API key is invalid.")
    print("Error details:", str(e))
    exit(1)
except openai.error.RateLimitError:
    print("⚠️ Rate limit hit during API test, but key appears valid.")
except Exception as e:
    print(f"❌ Unexpected error testing API key: {str(e)}")
    exit(1)

# File paths
json_path = "D:/Coding/ragfant/scrape/data/all_weekly_rankings.json"
output_path = "D:/Coding/ragfant/scrape/data/all_weekly_rankings_vectors.json"

print("\n📁 Loading player rankings data...")
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

print("🔄 Preparing texts for vectorization...")
# Build list of texts and associated metadata
texts_with_meta = []
for item in data:
    try:
        text = build_embedding_text(item)
        if text:
            texts_with_meta.append((text, item))
    except Exception as e:
        print(f"⚠️ Error processing item {item.get('player_name', 'Unknown')}: {e}")

print(f"📊 Found {len(texts_with_meta)} items to vectorize")

# Vectorize using OpenAI Embeddings API
vectors = []
rate_limit_retries = 0
max_retries = 5
retry_delay = 2

for text, item in tqdm(texts_with_meta, desc="Vectorizing"):
    success = False
    retries = 0
    
    while not success and retries < max_retries:
        try:
            response = openai.embeddings.create(
                input=text,
                model="text-embedding-ada-002"
            )
            success = True
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
        except openai.AuthenticationError as e:
            print(f"\n❌ Authentication Error: {str(e)}")
            print("Please check your API key and make sure it's a valid production key.")
            exit(1)
        except openai.error.RateLimitError:
            retries += 1
            rate_limit_retries += 1
            print(f"\n⏳ Rate limit hit, waiting {retry_delay * retries}s... (attempt {retries}/{max_retries})")
            time.sleep(retry_delay * retries)
        except Exception as e:
            print(f"\n❌ Embedding failed for {item['player_name']}: {e}")
            break

print(f"\n📈 Embedding Statistics:")
print(f"Total items processed: {len(texts_with_meta)}")
print(f"Successful embeddings: {len(vectors)}")
print(f"Rate limit retries: {rate_limit_retries}")

# Save vectors to file
print(f"\n💾 Saving vectors to {output_path}...")
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(vectors, f, indent=2)

print(f"✅ Successfully saved {len(vectors)} vectors to {output_path}")
