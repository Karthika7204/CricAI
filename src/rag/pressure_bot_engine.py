"""
pressure_bot_engine.py — Pressure Avoid Recommendation Bot
==========================================================
Standalone engine that identifies pressure points and provides tactical
advice on what to avoid and what to do for better performance.
"""

import json
import os
import pandas as pd
from pathlib import Path
from llm_connector import GeminiConnector
from prompt_builder import PromptBuilder
from pvp_analysis import get_pvp_comparison

class PressureBotEngine:
    """
    Analyzes match data to identify pressure points and provide 
    recommendations on performance improvement and risk avoidance.
    """

    def __init__(self, data_dir: str = "d:/CricAI/data", gemini_api_key: str = None):
        self.data_dir = Path(data_dir)
        try:
            self.llm = GeminiConnector(api_key=gemini_api_key)
        except Exception as e:
            print(f"Warning: Gemini initialization failed: {e}")
            self.llm = None

    def _load_json(self, path: Path):
        if not path.exists():
            return {}
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _get_previous_match_ids(self, match_id: str, teams: list) -> dict:
        """
        Finds the most recent match ID for each team before the current match.
        Returns: {team_name: match_id}
        """
        bat_path = self.data_dir / "raw" / "t20" / "ICC_Men_s_T20_World_Cup_batting.csv"
        if not bat_path.exists():
            return {}

        try:
            df = pd.read_csv(bat_path)
            # Find date of current match
            current_match = df[df['match_id'].astype(str) == str(match_id)]
            if current_match.empty:
                return {}
            
            current_date = current_match['date'].iloc[0]
            
            last_matches = {}
            for team in teams:
                # Find previous matches for THIS team
                team_prev = df[(df['team'] == team) & (df['date'] < current_date)]
                if not team_prev.empty:
                    latest_prev_date = team_prev['date'].max()
                    latest_match = team_prev[team_prev['date'] == latest_prev_date]
                    last_matches[team] = str(latest_match['match_id'].iloc[0])
            
            return last_matches
        except Exception as e:
            print(f"Error finding previous matches: {e}")
            return {}

    def query(self, match_id: str, user_query: str) -> dict:
        """
        Processes a pressure avoid recommendation query.
        """
        match_id = str(match_id)
        match_folder = self.data_dir / "processed" / "t20" / "matches" / match_id
        
        # Load Current Match Data
        current_summary = self._load_json(match_folder / "structured_summary.json")
        current_insights = self._load_json(match_folder / "pre_match_insights.json")
        
        if not current_summary:
            return {"error": "Current match summary data not found."}

        # Identify Teams
        teams = list(current_summary.get("match_context", {}).get("Teams", {}).keys())
        
        # Load Previous Match Data for each team
        prev_match_map = self._get_previous_match_ids(match_id, teams)
        prev_summaries = {}
        prev_insights = {}

        for team, p_match_id in prev_match_map.items():
            p_folder = self.data_dir / "processed" / "t20" / "matches" / p_match_id
            prev_summaries[team] = self._load_json(p_folder / "structured_summary.json")
            prev_insights[team] = self._load_json(p_folder / "pre_match_insights.json")

        # Load PvP Comparison Data (Integrate Strategy Bot context)
        pvp_data = get_pvp_comparison(match_id, str(self.data_dir))

        if not self.llm:
            return {
                "answer": "LLM not configured.", 
                "current_summary_available": True,
                "previous_match_ids": prev_match_map,
                "pvp_available": bool(pvp_data and "error" not in pvp_data)
            }

        prompt = PromptBuilder.build_pressure_recommendation_prompt(
            user_query, 
            current_summary, 
            prev_summaries, 
            pvp_data
        )
        answer = self.llm.generate_response(prompt)

        return {
            "match_id": match_id,
            "previous_match_id": next(iter(prev_match_map.values())) if prev_match_map else None,
            "previous_match_ids": prev_match_map,
            "answer": answer,
            "source": "pressure_recommendation_bot"
        }

if __name__ == "__main__":
    # Test stub
    bot = PressureBotEngine()
    res = bot.query("1512721", "What should the USA team avoid to perform better?")
    print(res.get("answer"))
