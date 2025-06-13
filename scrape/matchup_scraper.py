import requests
import re
import json
from bs4 import BeautifulSoup
import pandas as pd

def get_season_matchups(player_name, position):
    """Fetch season-long matchup data for a player from FantasyPros."""
    
    # Convert player name to URL format
    player_url = player_name.lower().replace(" ", "-")
    
    url = f"https://www.fantasypros.com/nfl/games/{player_url}.php"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the matchups table
        schedule_table = soup.find('table', {'class': 'player-table'})
        
        if not schedule_table:
            return None
            
        matchups = []
        
        # Parse table rows
        rows = schedule_table.find_all('tr')[1:]  # Skip header row
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 4:
                week = cols[0].text.strip()
                opponent = cols[1].text.strip()
                defense_rank = cols[2].text.strip()  # Defense rank vs position
                matchup_rating = cols[3].text.strip()  # Matchup rating
                
                matchups.append({
                    'week': week,
                    'opponent': opponent,
                    'defense_rank': defense_rank,
                    'matchup_rating': matchup_rating
                })
        
        return {
            'player_name': player_name,
            'position': position,
            'matchups': matchups
        }
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching matchups for {player_name}: {str(e)}")
        return None

def get_defense_rankings():
    """Get defensive rankings against each position."""
    url = "https://www.fantasypros.com/nfl/defense-vs-position.php"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        defense_data = {}
        
        # Find and parse the defense vs position tables for each position
        for position in ['QB', 'RB', 'WR', 'TE']:
            table_id = f'data-table-{position.lower()}'
            table = soup.find('table', {'id': table_id})
            
            if table:
                position_data = {}
                rows = table.find_all('tr')[1:]  # Skip header
                
                for row in rows:
                    cols = row.find_all('td')
                    if len(cols) >= 2:
                        team = cols[0].text.strip()
                        rank = cols[1].text.strip()
                        position_data[team] = rank
                
                defense_data[position] = position_data
        
        return defense_data
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching defense rankings: {str(e)}")
        return None
