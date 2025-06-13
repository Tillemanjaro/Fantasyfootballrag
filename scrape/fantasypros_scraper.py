import requests
import re
import json
import os

POSITIONS = {
    "QB": "https://www.fantasypros.com/nfl/rankings/qb.php",
    "RB": "https://www.fantasypros.com/nfl/rankings/rb.php",
    "WR": "https://www.fantasypros.com/nfl/rankings/wr.php",
    "TE": "https://www.fantasypros.com/nfl/rankings/te.php",
    "K":  "https://www.fantasypros.com/nfl/rankings/k.php",
    "DST": "https://www.fantasypros.com/nfl/rankings/dst.php",
}

def scrape_fantasypros_rankings(url, position):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error during requests to {url}: {str(e)}")
        return []

    match = re.search(r'var ecrData = (.*?);\n', response.text, re.DOTALL)
    if not match:
        print(f"ecrData not found in page for {position}.")
        return []

    ecr_json = match.group(1)
    try:
        ecr_data = json.loads(ecr_json)
    except Exception as e:
        print(f"Error parsing ecrData JSON for {position}: {e}")
        return []

    players = ecr_data.get("players", [])
    for p in players:
        p["scraped_position"] = position
    print(f"Scraped {len(players)} {position}s")
    return players

def save_to_json(data, path="data/all_weekly_rankings.json"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"✅ Saved {len(data)} players to {path}")

def get_rookie_data():
    """Scrape rookie-specific data from FantasyPros."""
    url = "https://www.fantasypros.com/nfl/rankings/rookies.php"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        # Extract rookie data from the page
        match = re.search(r'var ecrData = (.*?);\n', response.text, re.DOTALL)
        if not match:
            print("Rookie data not found in page.")
            return []

        rookie_data = json.loads(match.group(1))
        
        # Process and format rookie data
        rookies = []
        for player in rookie_data.get('players', []):
            rookie = {
                'player_name': player.get('player_name', ''),
                'position': player.get('position', ''),
                'team': player.get('team', ''),
                'ecr_rank': player.get('rank_ecr', 0),
                'pos_rank': player.get('pos_rank', ''),
                'college': player.get('player_college', ''),
                'draft_pick': player.get('notes', '').split('Pick ')[1].split(')')[0] if 'Pick ' in player.get('notes', '') else '',
                'experience': 'Rookie',
                'rookie': True,
                'notes': player.get('notes', '') + ' (2025 Draft)',
                'start_sit_grade': player.get('start_sit_grade', 'C')
            }
            rookies.append(rookie)
        
        return rookies
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching rookie data: {str(e)}")
        return []

if __name__ == "__main__":
    all_players = []
    for pos, url in POSITIONS.items():
        players = scrape_fantasypros_rankings(url, pos)
        all_players.extend(players)
        
    # Get rookie data and add to all players
    rookie_players = get_rookie_data()
    all_players.extend(rookie_players)
    
    save_to_json(all_players)