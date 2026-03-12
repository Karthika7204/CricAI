"""
strategy_bot_engine.py — Strategy Recommendation Bot
=====================================================
Standalone engine that provides tactical advice on bowler rotation 
and batting order based on match performance and matchups.
"""

import json
import os
import pandas as pd
from pathlib import Path
from llm_connector import GeminiConnector
from prompt_builder import PromptBuilder
from pvp_analysis import get_pvp_comparison

class StrategyBotEngine:
    """
    Analyzes match data to provide tactical strategy recommendations.
    Focuses on bowler rotation and batting order adjustments.
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
        with open(path, "r") as f:
            return json.load(f)

    def query(self, match_id: str, user_query: str) -> dict:
        """
        Processes a strategy query.
        """
        match_id = str(match_id)
        match_folder = self.data_dir / "processed" / "t20" / "matches" / match_id
        
        # Load Data Sources
        summary = self._load_json(match_folder / "structured_summary.json")
        pvp_data = get_pvp_comparison(match_id, str(self.data_dir))
        insights = self._load_json(match_folder / "pre_match_insights.json")

        if not summary:
            return {"error": "Match summary data not found."}

        # Contextual Filtering (Optional: we could filter pvp_data to reduce token usage)
        # For strategy, we usually want the top significant matchups and current match stats.
        
        if not self.llm:
            return {"answer": "LLM not configured.", "summary_available": bool(summary)}

        prompt = PromptBuilder.build_strategy_recommendation_prompt(user_query, summary, pvp_data, insights)
        answer = self.llm.generate_response(prompt)

        return {
            "match_id": match_id,
            "answer": answer,
            "source": "strategy_recommendation_bot"
        }
