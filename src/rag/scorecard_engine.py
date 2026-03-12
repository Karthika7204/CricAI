import pandas as pd
import os
from pathlib import Path

def get_match_scorecard(match_id, data_dir="d:/CricAI/data"):
    """
    Extracts full batting and bowling scorecard for a given match_id from raw CSV files.
    """
    match_id = int(match_id)
    batting_csv = Path(data_dir) / "raw" / "t20" / "ICC_Men_s_T20_World_Cup_batting.csv"
    bowling_csv = Path(data_dir) / "raw" / "t20" / "ICC_Men_s_T20_World_Cup_bowling.csv"

    if not batting_csv.exists() or not bowling_csv.exists():
        return {"error": "Scorecard CSV files not found."}

    try:
        # Load batting data
        df_bat = pd.read_csv(batting_csv)
        match_bat = df_bat[df_bat["match_id"] == match_id].copy()
        
        # Load bowling data
        df_bowl = pd.read_csv(bowling_csv)
        match_bowl = df_bowl[df_bowl["match_id"] == match_id].copy()

        if match_bat.empty and match_bowl.empty:
            return {"error": f"No scorecard data found for match {match_id}"}

        # Process Innings
        innings = {}
        for inn_num_np in sorted(match_bat["innings"].unique()):
            inn_num = int(inn_num_np)
            inn_bat = match_bat[match_bat["innings"] == inn_num]
            inn_bowl = match_bowl[match_bowl["innings"] == inn_num] # Opposing team bowled in this innings
            
            team_name = inn_bat["team"].iloc[0] if not inn_bat.empty else "Unknown"
            
            # Formatting batting
            batters = []
            for _, row in inn_bat.iterrows():
                dismissal = row["dismissal_kind"] if row["dismissed"] else "not out"
                batters.append({
                    "name": row["player"],
                    "runs": int(row["runs"]),
                    "balls": int(row["balls_faced"]),
                    "fours": int(row["fours"]),
                    "sixes": int(row["sixes"]),
                    "sr": float(row["strike_rate"]),
                    "out": str(dismissal)
                })

            # Formatting bowling (Wait, bowling in innings 1 is done by team in innings 2)
            # Actually, the CSV 'innings' column usually refers to which innings it was.
            # Usually, in these CSVs, innings 1 bowling is by the team that bats in innings 2.
            # Let's check who bowled in innings 1.
            
            innings[inn_num] = {
                "team": team_name,
                "batting": batters,
                "total_runs": int(inn_bat["runs"].sum()), # This is just a sum of players, not official total
                "wickets": int(inn_bat["dismissed"].sum())
            }

        # Now handle bowling properly
        # Bowling in Innings 1 belongs to the bowling card of that match phase
        for inn_num_np in sorted(match_bowl["innings"].unique()):
            inn_num = int(inn_num_np)
            inn_bowl = match_bowl[match_bowl["innings"] == inn_num]
            bowlers = []
            for _, row in inn_bowl.iterrows():
                bowlers.append({
                    "name": row["player"],
                    "overs": float(row["overs"]),
                    "maidens": int(row["maidens"]),
                    "runs": int(row["runs_conceded"]),
                    "wickets": int(row["wickets"]),
                    "econ": float(row["economy"])
                })
            
            if inn_num in innings:
                # The team that bowled in innings 1 is the one that bats in innings 2
                # But the UI usually shows Batting and Bowling of the SAME innings together?
                # No, often it's "Team A Batting" then "Team B Bowling" (who bowled to Team A).
                innings[inn_num]["bowling"] = bowlers

        return {
            "match_id": match_id,
            "innings": innings
        }

    except Exception as e:
        return {"error": f"Error processing scorecard: {str(e)}"}

if __name__ == "__main__":
    import json
    # Test with match 1512721
    res = get_match_scorecard(1512721)
    print(json.dumps(res, indent=2))
