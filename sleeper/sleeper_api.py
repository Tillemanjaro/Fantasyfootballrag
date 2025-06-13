import requests
from typing import Dict, List, Optional
import logging

class SleeperAPI:
    BASE_URL = "https://api.sleeper.app/v1"

    def __init__(self):
        self.session = requests.Session()
        self.logger = logging.getLogger(__name__)

    def get_user(self, username: str) -> Optional[Dict]:
        """Get user information by username."""
        response = self.session.get(f"{self.BASE_URL}/user/{username}")
        if response.status_code == 200:
            return response.json()
        self.logger.error(f"Failed to get user {username}: {response.status_code}")
        return None

    def get_user_leagues(self, user_id: str, season: str = "2025") -> List[Dict]:
        """Get all leagues for a user in a season."""
        response = self.session.get(f"{self.BASE_URL}/user/{user_id}/leagues/nfl/{season}")
        if response.status_code == 200:
            return response.json()
        self.logger.error(f"Failed to get leagues for user {user_id}: {response.status_code}")
        return []

    def get_all_leagues_for_user(self, user_id: str) -> Dict[str, List[Dict]]:
        """Get all leagues for a user across multiple seasons."""
        seasons = ["2023", "2024", "2025"]  # Add more seasons as needed
        leagues_by_season = {}
        for season in seasons:
            leagues = self.get_user_leagues(user_id, season)
            if leagues:
                leagues_by_season[season] = leagues
        return leagues_by_season

    def get_league(self, league_id: str) -> Optional[Dict]:
        """Get league information."""
        response = self.session.get(f"{self.BASE_URL}/league/{league_id}")
        if response.status_code == 200:
            return response.json()
        self.logger.error(f"Failed to get league {league_id}: {response.status_code}")
        return None

    def get_league_rosters(self, league_id: str) -> List[Dict]:
        """Get all rosters in a league."""
        response = self.session.get(f"{self.BASE_URL}/league/{league_id}/rosters")
        if response.status_code == 200:
            return response.json()
        self.logger.error(f"Failed to get rosters for league {league_id}: {response.status_code}")
        return []

    def get_league_users(self, league_id: str) -> List[Dict]:
        """Get all users in a league."""
        response = self.session.get(f"{self.BASE_URL}/league/{league_id}/users")
        if response.status_code == 200:
            return response.json()
        self.logger.error(f"Failed to get users for league {league_id}: {response.status_code}")
        return []

    def get_league_matchups(self, league_id: str, week: int) -> List[Dict]:
        """Get matchups for a specific week."""
        response = self.session.get(f"{self.BASE_URL}/league/{league_id}/matchups/{week}")
        if response.status_code == 200:
            return response.json()
        self.logger.error(f"Failed to get matchups for league {league_id} week {week}: {response.status_code}")
        return []

    def get_league_transactions(self, league_id: str, week: int) -> List[Dict]:
        """Get transactions for a specific week."""
        response = self.session.get(f"{self.BASE_URL}/league/{league_id}/transactions/{week}")
        if response.status_code == 200:
            return response.json()
        self.logger.error(f"Failed to get transactions for league {league_id} week {week}: {response.status_code}")
        return []

    def get_draft(self, draft_id: str) -> Optional[Dict]:
        """Get draft information."""
        response = self.session.get(f"{self.BASE_URL}/draft/{draft_id}")
        if response.status_code == 200:
            return response.json()
        self.logger.error(f"Failed to get draft {draft_id}: {response.status_code}")
        return None

    def get_draft_picks(self, draft_id: str) -> List[Dict]:
        """Get all picks in a draft."""
        response = self.session.get(f"{self.BASE_URL}/draft/{draft_id}/picks")
        if response.status_code == 200:
            return response.json()
        self.logger.error(f"Failed to get picks for draft {draft_id}: {response.status_code}")
        return []

    def get_traded_picks(self, league_id: str) -> List[Dict]:
        """Get traded draft picks in a league."""
        response = self.session.get(f"{self.BASE_URL}/league/{league_id}/traded_picks")
        if response.status_code == 200:
            return response.json()
        self.logger.error(f"Failed to get traded picks for league {league_id}: {response.status_code}")
        return []

    def get_all_players(self) -> Dict:
        """Get all NFL players."""
        response = self.session.get(f"{self.BASE_URL}/players/nfl")
        if response.status_code == 200:
            return response.json()
        self.logger.error("Failed to get NFL players")
        return {}

    def get_trending_players(self, type: str = "add", hours: int = 24, limit: int = 25) -> List[Dict]:
        """Get trending players (added/dropped)."""
        response = self.session.get(
            f"{self.BASE_URL}/players/nfl/trending/{type}",
            params={"lookback_hours": hours, "limit": limit}
        )
        if response.status_code == 200:
            return response.json()
        self.logger.error(f"Failed to get trending players: {response.status_code}")
        return []
