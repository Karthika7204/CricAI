import sys
import os
from pathlib import Path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src', 'rag'))

from insight_engine import PreMatchInsightEngine
import json

def test_match_direct(match_id, date, teams):
    print(f"\n--- Testing Match: {match_id} (Direct Engine Call) ---")
    try:
        engine = PreMatchInsightEngine()

        metadata = {
            "date": date,
            "teams": teams,
            "captains": {t: {"captain": "TBD"} for t in teams},
            "all_players": []
        }
        
        # Manually find players for debug
        for team in teams:
            p = engine._get_previous_match_players(team, date)
            print(f"  Players for {team} before {date}: {len(p)} found")
            if "Arshdeep Singh" in p:
                print(f"  ALERT: Arshdeep Singh found in {team} squad!")
            else:
                print(f"  OK: Arshdeep Singh not in {team} squad.")

        insights = engine.generate_insights(match_id, metadata)
        print(f"Ranking Races count: {len(insights.get('ranking_races', []))}")

    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Pakistan's 2nd match is 1512730 on 2026-02-10
    # Its previous match (team USA) was 1512721 (Ind vs USA)
    test_match_direct("1512730", "2026-02-10", ["Pakistan", "United States of America"])
