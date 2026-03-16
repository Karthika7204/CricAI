import os
import json
import datetime
import sys
import re

# Add src to path to import rag modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from flow.flow_builder import FlowBuilder
from flow.flow_prompt import RECOMMENDATION_SYSTEM_PROMPT, get_recommendation_prompt
from rag.llm_connector import GeminiConnector

class MatchRecommendEngine:
    """
    Coordinates the generation, caching, and loading of AI Match Recommendations.
    """
    def __init__(self, data_root="d:/CricAI/data/processed/t20/matches"):
        self.data_root = os.path.normpath(data_root)
        self.llm = GeminiConnector()

    def _get_match_path(self, match_id):
        return os.path.join(self.data_root, str(match_id))

    def _get_recommend_file_path(self, match_id):
        return os.path.join(self._get_match_path(match_id), "match_recommendations.json")

    def load_recommendations(self, match_id):
        """Returns cached recommendations if exists, else None."""
        path = self._get_recommend_file_path(match_id)
        if os.path.exists(path):
            with open(path, 'r') as f:
                return json.load(f)
        return None

    def save_recommendations(self, match_id, recommendations):
        """Saves generated recommendations to disk."""
        path = self._get_recommend_file_path(match_id)
        recommend_data = {
            "match_id": str(match_id),
            "generated_at": datetime.datetime.now().isoformat(),
            "recommendations": recommendations
        }
        with open(path, 'w') as f:
            json.dump(recommend_data, f, indent=2)
        return recommend_data

    def generate_recommendations(self, match_id):
        """Full pipeline: Extracted summary -> LLM -> Cache -> Return."""
        # Check cache first
        cached = self.load_recommendations(match_id)
        if cached:
            return cached

        # 1. Extraction
        match_path = self._get_match_path(match_id)
        builder = FlowBuilder(match_path)
        summary_json = builder.extract_summary_for_recommendations()

        if not summary_json:
            return {"error": f"No summary data found for match {match_id}"}

        # 2. AI Generation
        user_prompt = get_recommendation_prompt(summary_json)
        full_prompt = f"{RECOMMENDATION_SYSTEM_PROMPT}\n\n{user_prompt}"
        response_text = self.llm.generate_response(full_prompt)

        # 3. Parsing structure
        parsed_recommendations = self._parse_recommendations(response_text)

        # 4. Save and return
        return self.save_recommendations(match_id, parsed_recommendations)

    def _parse_recommendations(self, text):
        """
        Parses the LLM output into a dictionary of categories and points.
        """
        categories = [
            "Strategic Adjustments",
            "Batting Optimization",
            "Bowling Optimization",
            "Player Role Recommendations",
            "Pressure Management Insights",
            "Risk Alerts",
            "Future Preparation Focus"
        ]
        
        result = {}
        current_category = None
        
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check if line matches a category (allowing for emojis and formatting)
            matched_cat = None
            for cat in categories:
                if cat.lower() in line.lower() and ('###' in line or '🔹' in line):
                    matched_cat = cat
                    break
            
            if matched_cat:
                current_category = matched_cat
                result[current_category] = []
                continue
            
            if current_category and (line.startswith('•') or line.startswith('-') or line.startswith('*')):
                # Clean up bullet point
                point = re.sub(r'^[•\-*]\s*', '', line)
                result[current_category].append(point)
        
        # Fallback if parsing failed or categories are missing
        for cat in categories:
            if cat not in result:
                result[cat] = []
                
        return result

if __name__ == "__main__":
    engine = MatchRecommendEngine()
    # Test with match_id 1512721
    result = engine.generate_recommendations("1512743")
    print(json.dumps(result, indent=2))
