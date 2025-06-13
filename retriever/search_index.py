import os
import numpy as np
import faiss
import pickle
from dotenv import load_dotenv
from openai import OpenAI
from pathlib import Path

# Load API key and project ID
load_dotenv()
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    project=os.getenv("OPENAI_PROJECT_ID")
)

# Embedding function
def get_query_embedding(text):
    response = client.embeddings.create(
        model="text-embedding-ada-002",
        input=text
    )
    return np.array(response.data[0].embedding).astype("float32").reshape(1, -1)

# Format metadata into readable strings
def format_metadata(meta):
    grade_class = f"grade-{meta.get('start_sit_grade', 'F')[0]}"
    base_info = (
        f"{meta['player_name']} ({meta['position']} - {meta['team']}) "
        f"ECR Rank #{meta['ecr_rank']}, Start/Sit Grade: <span class='{grade_class}'>{meta.get('start_sit_grade', 'N/A')}</span>, "
        f"Position Rank: {meta.get('pos_rank', 'N/A')}"
    )
    
    # Add matchup information if available
    matchups_info = ""
    if 'matchups' in meta:
        upcoming_matchups = meta['matchups'][:5]  # Next 5 games
        matchups_info = "\nUpcoming matchups:\n"
        for matchup in upcoming_matchups:
            rating_class = 'grade-' + ('A' if float(matchup['matchup_rating']) >= 4 
                                     else 'B' if float(matchup['matchup_rating']) >= 3 
                                     else 'C')
            matchups_info += (f"Week {matchup['week']}: vs {matchup['opponent']} "
                            f"(Def Rank: {matchup['defense_rank']}, "
                            f"Matchup Rating: <span class='{rating_class}'>{matchup['matchup_rating']}</span>)\n")
    
    return base_info + matchups_info

def grade_to_number(grade):
    """Convert letter grade to numeric value for comparison"""
    if not grade:
        return -1
    grade_map = {
        'A+': 12, 'A': 11, 'A-': 10,
        'B+': 9, 'B': 8, 'B-': 7,
        'C+': 6, 'C': 5, 'C-': 4,
        'D+': 3, 'D': 2, 'D-': 1,
        'F': 0
    }
    return grade_map.get(grade, -1)

def search_index(query, documents=None, top_k=25, positions=None, min_grade=None):
    """
    Search the FAISS index with position and grade filters
    
    Args:
        query (str): The search query
        documents (list, optional): List of documents to search through
        top_k (int, optional): Number of results to return. Defaults to 25
        positions (list, optional): List of positions to filter by (e.g., ['QB', 'RB'])
        min_grade (str, optional): Minimum grade to include (e.g., 'B')
    """
    print("🔍 Searching for:", query)
    print(f"📊 Filters - Positions: {positions}, Min Grade: {min_grade}")
    
    # Determine if this is a lineup/draft question
    is_lineup_question = any(keyword in query.lower() for keyword in [
        "lineup", "draft", "pick", "roster", "team", "start", "bench", "flex"
    ])

    query_vector = get_query_embedding(query)

    # Get absolute paths
    base_dir = Path(__file__).parent.parent
    index_path = base_dir / "data" / "fantasy_index.faiss"
    metadata_path = base_dir / "data" / "fantasy_metadata.pkl"

    print(f"📁 Loading index from: {index_path}")
    print(f"📁 Loading metadata from: {metadata_path}")

    # Load index and metadata
    index = faiss.read_index(str(index_path))
    with open(metadata_path, "rb") as f:
        metadata = pickle.load(f)

    # Normalize query
    faiss.normalize_L2(query_vector)

    # Search more results initially to allow for filtering
    k_search = max(100, top_k * 2)
    D, I = index.search(query_vector, k_search)
    
    results = []
    seen_positions = set()
    min_grade_value = grade_to_number(min_grade) if min_grade else -1
    
    # Process and filter results
    candidates = []
    for i, score in zip(I[0], D[0]):
        if i < 0:  # Invalid index
            continue
            
        meta = metadata[i]
        pos = meta['position']
        grade = meta.get('start_sit_grade', 'F')
        grade_value = grade_to_number(grade)
        
        # Apply filters
        if positions and pos not in positions:
            continue
        if min_grade and grade_value < min_grade_value:
            continue
            
        # For lineup questions, prioritize by grade and rank
        if is_lineup_question:
            rank = int(meta['ecr_rank'])
            grade_score = grade_to_number(grade)
            candidates.append((i, score, grade_score, rank, pos))
        else:
            candidates.append((i, score, 0, 0, pos))
    
    # Sort results
    if is_lineup_question:
        candidates.sort(key=lambda x: (-x[2], x[3]))  # Sort by grade (high to low) then rank (low to high)
    
    # Build final results list
    pos_counts = {pos: 0 for pos in ['QB', 'RB', 'WR', 'TE', 'K', 'DST']}
    for i, score, _, _, pos in candidates:
        if is_lineup_question and pos_counts[pos] >= 5:
            continue
        
        results.append(f"{format_metadata(metadata[i])} (Score: {score:.3f})")
        pos_counts[pos] += 1
        
        if len(results) >= top_k:
            break
    
    print(f"✨ Found {len(results)} results")
    return results

def filter_rookies(metadata_list):
    """Filter metadata to only include rookie players."""
    rookies = []
    for meta in metadata_list:
        # Check for rookie indicators in metadata
        is_rookie = (
            meta.get('experience', '').lower() == 'rookie' or
            meta.get('rookie', False) or
            '(R)' in meta.get('notes', '') or
            '2025 Draft' in meta.get('notes', '') or
            'Rookie' in meta.get('notes', '')
        )
        if is_rookie:
            rookies.append(meta)
    return rookies

def search_index(query, top_k=5):
    # Load the index and metadata
    index_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'fantasy_index.faiss')
    metadata_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'fantasy_metadata.pkl')
    
    if not os.path.exists(index_path) or not os.path.exists(metadata_path):
        return ["Error: Fantasy football data not found. Please ensure the data files are present."]
    
    # Load index and metadata
    index = faiss.read_index(index_path)
    with open(metadata_path, 'rb') as f:
        metadata = pickle.load(f)
    
    # Check if this is a rookie-specific query
    is_rookie_query = any(word in query.lower() for word in ['rookie', 'rookies', '2025 draft', 'first year', 'new players'])
    
    # Get query embedding
    query_vector = get_query_embedding(query)
    
    # Search with larger k if looking for rookies to ensure we find enough rookie players
    search_k = top_k * 3 if is_rookie_query else top_k
    D, I = index.search(query_vector, search_k)
    
    # Format results
    results = []
    for idx in I[0]:
        if idx != -1:  # Valid index
            meta = metadata[idx]
            # Get matchup data for the player if not already present
            if 'matchups' not in meta:
                from scrape.matchup_scraper import get_season_matchups
                matchup_data = get_season_matchups(meta['player_name'], meta['position'])
                if matchup_data:
                    meta['matchups'] = matchup_data['matchups']
            results.append(meta)
    
    # Filter for rookies if it's a rookie query
    if is_rookie_query:
        results = filter_rookies(results)
        # Limit to top_k after filtering
        results = results[:top_k]
    
    # Format the final results
    return [format_metadata(meta) for meta in results]
