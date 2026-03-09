import os
import json
import datetime
import sys

# Add src to path to import rag modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from flow.flow_builder import FlowBuilder
from flow.flow_prompt import SYSTEM_PROMPT, get_match_flow_prompt
from rag.llm_connector import GeminiConnector

class MatchFlowEngine:
    """
    Coordinates the generation, caching, and loading of AI Match Flow.
    """
    def __init__(self, data_root="d:/CricAI/data/processed/t20/matches"):
        self.data_root = os.path.normpath(data_root)
        self.llm = GeminiConnector()

    def _get_match_path(self, match_id):
        return os.path.join(self.data_root, str(match_id))

    def _get_flow_file_path(self, match_id):
        return os.path.join(self._get_match_path(match_id), "match_flow.json")

    def load_match_flow(self, match_id):
        """Returns cached flow if exists, else None."""
        path = self._get_flow_file_path(match_id)
        if os.path.exists(path):
            with open(path, 'r') as f:
                return json.load(f)
        return None

    def save_match_flow(self, match_id, flow_points):
        """Saves generated flow to disk."""
        path = self._get_flow_file_path(match_id)
        flow_data = {
            "match_id": str(match_id),
            "generated_at": datetime.datetime.now().isoformat(),
            "flow_points": flow_points
        }
        with open(path, 'w') as f:
            json.dump(flow_data, f, indent=2)
        return flow_data

    def generate_match_flow(self, match_id):
        """Full pipeline: Extracted events -> LLM -> Cache -> Return."""
        # Check cache first
        cached = self.load_match_flow(match_id)
        if cached:
            return cached

        # 1. Extraction
        match_path = self._get_match_path(match_id)
        builder = FlowBuilder(match_path)
        events = builder.extract_events()

        if not events:
            return {"error": f"No summary data found for match {match_id}"}

        # 2. AI Compression
        events_json = json.dumps(events, indent=2)
        user_prompt = get_match_flow_prompt(events_json)
        
        full_prompt = f"{SYSTEM_PROMPT}\n\n{user_prompt}"
        response_text = self.llm.generate_response(full_prompt)

        # 3. Parsing bullet points
        flow_points = [
            line.strip("*- ").strip() 
            for line in response_text.split('\n') 
            if line.strip() and (line.strip().startswith('•') or line.strip().startswith('-') or line.strip().startswith('*') or (len(line) > 10 and not line.startswith('Here are')) )
        ]

        # Cleanup if LLM returns a list with numbers
        if not flow_points:
             flow_points = [line.strip() for line in response_text.split('\n') if line.strip() and len(line) > 10]

        # 4. Save and return
        return self.save_match_flow(match_id, flow_points)

if __name__ == "__main__":
    engine = MatchFlowEngine()
    # Test with match_id 1512721
    result = engine.generate_match_flow("1512721")
    print(json.dumps(result, indent=2))
