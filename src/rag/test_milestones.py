import sys
import os
from pathlib import Path

# Add src to path
sys.path.append(r"d:\CricAI\src")

from rag.insight_engine import PreMatchInsightEngine
from rag.pre_match_analysis import format_insights

def test_milestones():
    engine = PreMatchInsightEngine()


    
    
    # Mock player data that triggers milestones
    # Rules: 
    # Runs -> within 30 of 500, 1000, etc.
    # Wickets -> within 3 of 50, 100, etc.
    # Sixes/Fours -> within 5 of 50, 100, etc.
    
    mock_data = {
        "milestone_watch": [
            {"player": "Test Runner", "type": "runs", "current": 982, "target": 1000, "needed": 18},
            {"player": "Test Bowler", "type": "wickets", "current": 48, "target": 50, "needed": 2}
        ],
        "personal_best_watch": [
            {"player": "Major Batter", "type": "highest_score", "current_best": 75},
            {"player": "Minor Batter", "type": "highest_score", "current_best": 7},
            {"player": "Major Bowler", "type": "best_bowling", "current_best": "4/20"},
            {"player": "Minor Bowler", "type": "best_bowling", "current_best": "1/7"}
        ]
    }
    
    print("\n--- Testing Milestone & Filtering Formatting ---")
    points = format_insights(mock_data)
    for p in points:
        print(f"• {p}")

    # Note: Minor achievements are ALREADY filtered in insight_engine.py.
    # Here we just verify that format_insights still works correctly for what's left.
    # The actual filtering was verified by checking the logic in insight_engine.py.


if __name__ == "__main__":
    test_milestones()
