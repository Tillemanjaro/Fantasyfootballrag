import json
import os
from fantasypros_scraper import get_rookie_data
from vectorize_with_gpt4 import vectorize_data

def update_rookie_data():
    """Update the fantasy rankings data with rookie information."""
    # Get the path to the rankings file
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    rankings_file = os.path.join(data_dir, 'all_weekly_rankings.json')
    
    # Create data directory if it doesn't exist
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    # Load existing rankings if available
    if os.path.exists(rankings_file):
        with open(rankings_file, 'r') as f:
            rankings_data = json.load(f)
    else:
        rankings_data = []
    
    # Get rookie data
    print("Fetching rookie data...")
    rookies = get_rookie_data()
    
    # Add rookie flag to existing players
    for player in rankings_data:
        player['rookie'] = False
    
    # Add rookies to the rankings data
    for rookie in rookies:
        # Check if rookie already exists in data
        exists = any(p['player_name'] == rookie['player_name'] for p in rankings_data)
        if not exists:
            rankings_data.append(rookie)
    
    # Save updated rankings
    print(f"Saving {len(rankings_data)} players ({len(rookies)} rookies)...")
    with open(rankings_file, 'w') as f:
        json.dump(rankings_data, f, indent=2)
    
    # Vectorize the updated data
    print("Vectorizing updated data...")
    vectorize_data(rankings_file)
    
    print("Rookie data update complete!")

if __name__ == "__main__":
    update_rookie_data()
