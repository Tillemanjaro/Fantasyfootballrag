from typing import Dict, List, Optional
from .sleeper_api import SleeperAPI

class SleeperLeagueManager:
    def __init__(self):
        self.api = SleeperAPI()
        self.current_season = "2025"
        self.all_players = None

    def get_user_leagues_info(self, username: str) -> Dict:
        """Get all relevant information for a user's leagues."""
        user = self.api.get_user(username)
        if not user:
            return {"error": f"User {username} not found"}

        user_id = user["user_id"]
        all_leagues = self.api.get_all_leagues_for_user(user_id)
        
        leagues_info = []
        for season, leagues in all_leagues.items():
            for league in leagues:
                league_id = league["league_id"]
                rosters = self.api.get_league_rosters(league_id)
                users = self.api.get_league_users(league_id)
                
                # Find user's roster
                user_roster = next(
                    (roster for roster in rosters if str(roster["owner_id"]) == str(user_id)),
                    None
                )

                if user_roster:
                    # Get draft information
                    draft_id = league.get("draft_id")
                    draft_info = None
                    if draft_id:
                        draft_info = self.api.get_draft(draft_id)
                        draft_picks = self.api.get_draft_picks(draft_id)
                        
                        # Add draft pick information to roster
                        user_picks = [
                            pick for pick in draft_picks
                            if str(pick.get("picked_by")) == str(user_id)
                        ]
                        user_roster["draft_picks"] = user_picks

                    leagues_info.append({
                        "season": season,
                        "league_name": league["name"],
                        "league_id": league_id,
                        "total_rosters": len(rosters),
                        "scoring_settings": league["scoring_settings"],
                        "roster_positions": league["roster_positions"],
                        "user_roster": user_roster,
                        "draft_info": draft_info
                    })

        return {
            "username": username,
            "user_id": user_id,
            "leagues": leagues_info
        }

    def get_roster_players(self, roster: Dict, include_draft_info: bool = True) -> List[Dict]:
        """Convert roster player IDs to player information."""
        if self.all_players is None:
            self.all_players = self.api.get_all_players()

        players = []
        for player_id in roster.get("players", []):
            if player_id in self.all_players:
                player = self.all_players[player_id].copy()
                
                # Add draft information if available
                if include_draft_info and "draft_picks" in roster:
                    draft_pick = next(
                        (pick for pick in roster["draft_picks"] if pick["player_id"] == player_id),
                        None
                    )
                    if draft_pick:
                        player["draft_round"] = draft_pick["round"]
                        player["draft_pick"] = draft_pick["pick_no"]

                players.append({
                    "player_id": player_id,
                    "full_name": player.get("full_name"),
                    "position": player.get("position"),
                    "team": player.get("team"),
                    "status": player.get("status"),
                    "injury_status": player.get("injury_status"),
                    "draft_info": {
                        "round": player.get("draft_round"),
                        "pick": player.get("draft_pick")
                    } if "draft_round" in player else None
                })

        return players

    def get_keeper_recommendations(self, league_id: str, user_id: str) -> List[Dict]:
        """Get keeper recommendations based on draft position and current rankings."""
        rosters = self.api.get_league_rosters(league_id)
        user_roster = next(
            (roster for roster in rosters if str(roster["owner_id"]) == str(user_id)),
            None
        )
        
        if not user_roster:
            return []

        players = self.get_roster_players(user_roster, include_draft_info=True)
        
        # Sort players by value (current ranking vs draft position)
        keeper_options = []
        for player in players:
            if player["draft_info"]:
                draft_round = player["draft_info"]["round"]
                keeper_round = max(1, draft_round - 1)  # One round better than draft position
                
                keeper_options.append({
                    "player": player,
                    "original_round": draft_round,
                    "keeper_round": keeper_round,
                    "value_score": self._calculate_keeper_value(player, keeper_round)
                })

        # Sort by value score
        keeper_options.sort(key=lambda x: x["value_score"], reverse=True)
        return keeper_options

    def _calculate_keeper_value(self, player: Dict, keeper_round: int) -> float:
        """Calculate a value score for a keeper based on position and draft round."""
        # This is a simple calculation - you might want to make it more sophisticated
        position_multipliers = {
            "QB": 1.0,
            "RB": 1.2,
            "WR": 1.1,
            "TE": 0.9,
            "K": 0.5,
            "DEF": 0.5
        }
        
        position_value = position_multipliers.get(player["position"], 1.0)
        round_value = (18 - keeper_round) / 17  # Assumes 17 rounds, higher value for earlier rounds
        
        return position_value * round_value

    def get_league_standings(self, league_id: str) -> List[Dict]:
        """Get current standings for a league."""
        rosters = self.api.get_league_rosters(league_id)
        users = {user["user_id"]: user for user in self.api.get_league_users(league_id)}
        
        standings = []
        for roster in rosters:
            user = users.get(str(roster["owner_id"]), {})
            standings.append({
                "user_id": roster["owner_id"],
                "username": user.get("display_name"),
                "team_name": roster.get("team_name"),
                "wins": roster.get("settings", {}).get("wins", 0),
                "losses": roster.get("settings", {}).get("losses", 0),
                "points_for": roster.get("settings", {}).get("fpts", 0),
                "points_against": roster.get("settings", {}).get("fpts_against", 0)
            })
        
        # Sort by wins, then points
        standings.sort(key=lambda x: (x["wins"], x["points_for"]), reverse=True)
        return standings

    def get_trade_picks(self, league_id: str) -> List[Dict]:
        """Get information about traded draft picks."""
        return self.api.get_traded_picks(league_id)

    def get_trending_players(self, hours: int = 24, limit: int = 25) -> Dict[str, List[Dict]]:
        """Get trending adds and drops."""
        return {
            "adds": self.api.get_trending_players("add", hours, limit),
            "drops": self.api.get_trending_players("drop", hours, limit)
        }
