import os
import sys
import json
import pickle
from pathlib import Path

# Add src to path to import rag modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from rag.insight_engine import PreMatchInsightEngine, calculate_pre_match_insights

def format_insights(data):
    """
    Converts structured insight data into human-readable sentences.
    """
    points = []
    
    # 1. Ranking Races
    for race in data.get("ranking_races", []):
        cat = race['category'].replace('_', ' ').title()
        effort = race.get('effort_needed', f"{race.get('points_away', '?')} points")
        points.append(f"{race['player']} needs {effort} to reach Rank {race['target_pos']} in ICC T20I {cat} rankings.")
    
    # 2. Milestones
    for ms in data.get("milestone_watch", []):
        type_label = ms['type']
        needed_label = ms['type']
        if ms['needed'] == 1:
            # Handle singular for six/four
            if ms['type'] in ['sixes', 'fours']:
                needed_label = ms['type'].rstrip('es').rstrip('s')
        
        if ms['type'] == 'runs':
             points.append(f"{ms['player']} is {ms['needed']} runs away from {ms['target']} T20I runs.")
        elif ms['type'] == 'wickets':
             points.append(f"{ms['player']} needs {ms['needed']} {'wicket' if ms['needed'] == 1 else 'wickets'} to reach {ms['target']} T20I wickets.")
        else: # Sixes or Fours
             points.append(f"{ms['player']} is {ms['needed']} {needed_label} away from {ms['target']} international {ms['type']}.")
        
    # 3. Personal Bests (REMOVED per user request)
    # This section was removed as it was providing "basic" highlights.
        
    return points

def get_pre_match_analysis(match_id, data_dir="d:/CricAI/data", force_refresh=False):
    """
    Direct data endpoint for frontend to fetch pre-match insights.
    Returns a dictionary containing raw data and textual explanations.
    """
    match_id = str(match_id)
    insight_file = Path(data_dir) / "processed" / "t20" / "matches" / match_id / "pre_match_insights.json"
    
    data = {}
    # Load or generate data
    if insight_file.exists() and not force_refresh:
        with open(insight_file, 'r') as f:
            data = json.load(f)
    else:
        try:
            data = calculate_pre_match_insights(match_id, data_dir)
        except Exception as e:
            data = {"match_id": match_id, "error": str(e)}

    # Add textual explanations
    textual_points = format_insights(data)
    
    return {
        "match_id": match_id,
        "data": data,
        "textual_insights": textual_points
    }

if __name__ == "__main__":
    # If run as a script: python pre_match_analysis.py <match_id>
    if len(sys.argv) > 1:
        match_id = sys.argv[1]
        result = get_pre_match_analysis(match_id, force_refresh=True)
        # For terminal output, print the list of strings as clear bullet points
        print(f"\n--- PRE-MATCH INSIGHTS FOR MATCH {match_id} ---\n")
        for point in result["textual_insights"]:
            print(f"• {point}")
        
        if "error" in result["data"]:
            print(f"ERROR: {result['data']['error']}")
            
        if not result["textual_insights"]:
            print("No significant insights found for this match.")
    else:
        print("Usage: python pre_match_analysis.py <match_id>")
