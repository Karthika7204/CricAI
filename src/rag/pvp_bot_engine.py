"""
pvp_bot_engine.py — Conversational PvP Recommendation Bot
==========================================================
Standalone wrapper that provides natural language recommendations
based on the pre-computed PvP data.

Uses Gemini to translate raw stats into tactical advice.
"""

import json
import os
import re
import pandas as pd
from pathlib import Path
from llm_connector import GeminiConnector
from prompt_builder import PromptBuilder
from pvp_analysis import get_pvp_comparison

class PvPBotEngine:
    """
    Conversational bot for Player vs Player recommendations.
    Provides English-understandable advice by comparing teammates 
    and identifying specific threats/opportunities.
    """

    def __init__(self, data_dir: str = "d:/CricAI/data", gemini_api_key: str = None):
        self.data_dir = Path(data_dir)
        try:
            self.llm = GeminiConnector(api_key=gemini_api_key)
        except Exception as e:
            print(f"Warning: Gemini initialization failed: {e}")
            self.llm = None
        
        # Load career data for name resolution
        career_path = self.data_dir / "processed" / "career" / "t20_master.parquet"
        if career_path.exists():
            self.df_names = pd.read_parquet(career_path)[["player_name", "full_name", "country"]]
        else:
            self.df_names = None

    def _resolve_names(self, user_query: str, players_in_match: list) -> list:
        """
        Maps natural language names to the specific names used in the match data.
        Example: "Surya Kumar Yadav" -> "SA Yadav"
        """
        user_query = user_query.lower()
        matched = set()
        
        for player in players_in_match:
            # 1. Direct match (e.g. "SA Yadav" in query)
            if player.lower() in user_query:
                matched.add(player)
                continue
                
            # 2. Career mapping (Full name check)
            if self.df_names is not None:
                # Find the row for this abbreviated match name
                row = self.df_names[self.df_names["player_name"] == player]
                if not row.empty:
                    full_name = str(row.iloc[0]["full_name"]).lower()
                    # Check if full name or parts of it are in the query
                    if full_name in user_query:
                        matched.add(player)
                    else:
                        # Check partial: "Surya" in "Suryakumar Ashok Yadav"
                        parts = full_name.replace("-", " ").split()
                        for p in parts:
                            if len(p) > 3 and p in user_query:
                                matched.add(player)
                                break

        return list(matched)

    def query(self, match_id: str, user_query: str) -> dict:
        """
        Processes a recommendation query with strict team/opposition focus.
        """
        match_id = str(match_id)
        pvp_data = get_pvp_comparison(match_id, str(self.data_dir))
        
        if "error" in pvp_data:
            return {"error": pvp_data["error"]}

        matchups = pvp_data.get("matchups", [])
        team_a = pvp_data.get("team_a")
        team_b = pvp_data.get("team_b")
        
        match_players = list(set([m["bat"] for m in matchups] + [m["bowl"] for m in matchups]))
        mentioned_players = self._resolve_names(user_query, match_players)
        
        lower_query = user_query.lower()
        mentioned_teams = []
        if team_a.lower() in lower_query: mentioned_teams.append(team_a)
        if team_b.lower() in lower_query: mentioned_teams.append(team_b)

        # 2. Filter Matchups (Strict Opposition Focus)
        filtered_matchups = []
        
        if mentioned_players:
            for p in mentioned_players:
                # Find side of the player
                p_side_bat = [m for m in matchups if m["bat"] == p]
                p_side_bowl = [m["bowl_t"] for m in matchups if m["bowl"] == p]
                
                # If they are primarily batting in mentioned context or available matchups
                if p_side_bat:
                    # Focus on their batting matchups (strictly vs opposition)
                    filtered_matchups.extend(p_side_bat)
                elif p_side_bowl:
                    # Focus on their bowling matchups (strictly vs opposition)
                    bowl_matchups = [m for m in matchups if m["bowl"] == p]
                    filtered_matchups.extend(bowl_matchups)

        if mentioned_teams:
            for t in mentioned_teams:
                # Top matchups for this team (already strictly vs opponent in engine)
                t_matchups = [m for m in matchups if m["bat_t"] == t or m["bowl_t"] == t]
                filtered_matchups.extend(t_matchups[:15])

        if not filtered_matchups:
            filtered_matchups = matchups[:20]

        # De-duplicate
        unique_matchups_dict = { (m["bat"], m["bowl"]): m for m in filtered_matchups }
        unique_matchups = list(unique_matchups_dict.values())

        # 3. LLM Reasoning
        if not self.llm:
            return {"answer": "No LLM configured.", "matchups": unique_matchups[:5]}

        prompt = PromptBuilder.build_pvp_recommendation_prompt(user_query, unique_matchups)
        answer = self.llm.generate_response(prompt)

        return {
            "match_id": match_id,
            "answer": answer,
            "source": "pvp_recommendation_bot",
            "resolved": {"players": mentioned_players, "teams": mentioned_teams},
            "data_count": len(unique_matchups)
        }

if __name__ == "__main__":
    # Test stub
    bot = PvPBotEngine()
    res = bot.query("1512721", "Who is good and bad against Surya Kumar Yadav?")
    print(res.get("answer"))
