import pandas as pd
import os
import json
from pathlib import Path

class PreMatchInsightEngine:
    """
    Generates predictive pre-match insights based on:
    1. ICC Rankings (Batting, Bowling, All-rounders)
    2. Player Career Stats (Batting & Bowling)
    3. Match Metadata (Players involved)
    """

    def __init__(self, data_dir="d:/CricAI/data"):
        self.data_dir = Path(data_dir)
        self.rankings_dir = self.data_dir / "raw" / "ICC Ranking" / "t20"
        self.career_dir = self.data_dir / "raw" / "career" / "t20"

    def _load_rankings(self):
        rankings = {
            "batting": pd.read_csv(self.rankings_dir / "icc_batting_t20i_men.csv"),
            "bowling": pd.read_csv(self.rankings_dir / "icc_bowling_t20i_men.csv"),
            "all_rounder": pd.read_csv(self.rankings_dir / "icc_all-rounder_t20i_men.csv")
        }
        
        # Pre-clean the rankings data for robust lookup
        for cat in rankings:
            df = rankings[cat]
            if 'pos' in df.columns:
                # Extract digits and convert to int
                df['pos_int'] = df['pos'].astype(str).str.extract(r'(\d+)').fillna(999).astype(int)
            if 'points' in df.columns:
                df['points_int'] = df['points'].astype(str).str.extract(r'(\d+)').fillna(0).astype(int)
                
        return rankings

    def _get_player_career(self, player_name, country, activity="batting"):
        # Normalize country names for file mapping
        c_norm = country.replace(' ', '_')
        possible_countries = [c_norm]
        if "United_States" in c_norm:
            possible_countries.extend(["United_States", "United_States_of_America"])
            
        # Possible file name formats depending on how the scraper saved them
        possible_filenames = [
            f"{c}_all_players_career.csv" for c in possible_countries
        ] + [
            f"{c}_all_players_career_{activity}.csv" for c in possible_countries
        ] + [
            f"{c}_all_players_career_t20.csv" for c in possible_countries
        ]
        
        for file_name in possible_filenames:
            path = self.career_dir / activity / file_name
            if path.exists():
                df = pd.read_csv(path)
                player_stats = df[df['player_name'] == player_name]
                if not player_stats.empty:
                    return player_stats.iloc[0].to_dict()
        return None

    def _get_previous_match_players(self, team, current_date):
        """
        Finds players from the previous match of the given team.
        """
        bat_path = self.data_dir / "raw" / "t20" / "ICC_Men_s_T20_World_Cup_batting.csv"
        bowl_path = self.data_dir / "raw" / "t20" / "ICC_Men_s_T20_World_Cup_bowling.csv"
        
        players = set()
        
        if bat_path.exists():
            df = pd.read_csv(bat_path)
            # Filter for previous matches
            prev_matches = df[(df['team'] == team) & (df['date'] < current_date)]
            if not prev_matches.empty:
                # Get most recent match
                last_date = prev_matches['date'].max()
                last_matches = prev_matches[prev_matches['date'] == last_date]
                last_id = last_matches['match_id'].max()
                # ONLY get players who played FOR this team in that match
                players.update(df[(df['match_id'] == last_id) & (df['team'] == team)]['player'].unique())
        
        if bowl_path.exists():
            df = pd.read_csv(bowl_path)
            prev_matches = df[(df['team'] == team) & (df['date'] < current_date)]
            if not prev_matches.empty:
                last_date = prev_matches['date'].max()
                last_matches = prev_matches[prev_matches['date'] == last_date]
                last_id = last_matches['match_id'].max()
                # ONLY get players who played FOR this team in that match
                players.update(df[(df['match_id'] == last_id) & (df['team'] == team)]['player'].unique())
                
        return list(players)

    def generate_insights(self, match_id, metadata):
        """
        Main entry point to generate insights JSON.
        """
        match_id = str(match_id)
        match_folder = self.data_dir / "processed" / "t20" / "matches" / match_id
        summary_path = match_folder / "structured_summary.json"
        
        match_players = []
        teams = list(metadata.get("captains", {}).keys()) if "captains" in metadata else []
        current_date = metadata.get("date", "2099-01-01")
        
        if summary_path.exists():
            with open(summary_path, 'r') as f:
                data = json.load(f)
                current_date = data.get("match_context", {}).get("date", current_date)
                teams = list(data.get("match_context", {}).get("Teams", {}).keys())
        
        # Fallback for teams if missing
        if not teams:
            bat_csv = match_folder / "batting.csv"
            if bat_csv.exists():
                bat_df = pd.read_csv(bat_csv)
                if 'team' in bat_df.columns:
                    teams = bat_df['team'].dropna().unique().tolist()
        
        # Get players from PREVIOUS matches of these teams
        for team in teams:
            prev_players = self._get_previous_match_players(team, current_date)
            if prev_players:
                match_players.extend(prev_players)
        
        # Fallback to current match players if no previous match found (or first match)
        if not match_players:
            match_players = metadata.get("all_players", [])
            # Fallback to structured summary
            if not match_players and summary_path.exists():
                with open(summary_path, 'r') as f:
                    data = json.load(f)
                    match_players = list(set([imp['player'] for imp in data.get('Detailed_Impact_Analysis', [])]))
            
            # FINAL FALLBACK: check batting.csv in match folder
            if not match_players:
                bat_csv = match_folder / "batting.csv"
                if bat_csv.exists():
                    bat_df = pd.read_csv(bat_csv)
                    if 'player' in bat_df.columns:
                        match_players = bat_df['player'].dropna().unique().tolist()

        match_players = list(set(match_players)) # Unique list
        # print(f"DEBUG: match_players: {len(match_players)} players found")

        rankings = self._load_rankings()
        insights = {
            "match_id": match_id,
            "ranking_races": [],
            "milestone_watch": [],
            "personal_best_watch": []
        }
        
        all_possible_milestones = []

        for player_name in match_players:
            # 1. Ranking Races
            for category, df in rankings.items():
                # Matching with strip and lower case for robustness
                match_df = df[df['player'].str.strip().str.lower() == player_name.strip().lower()]
                if not match_df.empty:
                    row = match_df.iloc[0]
                    pos = row['pos_int']
                    points = row['points_int']
                    # print(f"DEBUG: Found {player_name} in {category} rankings at pos {pos}")
                    
                    if pos > 100: continue # Only track Top 100 players
                    
                    # 1a. Proximity to Elite Milestones (Rank 1, 3, 5, 10)
                    for target in [1, 3, 5, 10]:
                        if pos > target:
                            target_row = df[df['pos_int'] == target]
                            if not target_row.empty:
                                target_points = target_row.iloc[0]['points_int']
                                gap = target_points - points
                                # Only show if gap is relatively small (within 60 points)
                                if 0 < gap <= 60:
                                    effort = ""
                                    if category == "batting":
                                        effort = f"{int(gap * 1.5)} runs"
                                    elif category == "bowling":
                                        effort = f"{max(1, int(gap / 13))} wickets"
                                    else: # all_rounder
                                        effort = f"{int(gap * 1.5)} runs or {max(1, int(gap / 13))} {'wicket' if max(1, int(gap / 13)) == 1 else 'wickets'}"

                                    insights["ranking_races"].append({
                                        "player": player_name,
                                        "category": category,
                                        "current_pos": int(pos),
                                        "target_pos": int(target),
                                        "points_away": int(gap),
                                        "effort_needed": effort
                                    })
                                    break # Only show the nearest milestone jump

            # Determine player country (hacky lookup for now)
            player_country = None
            if "team_mapping" in metadata:
                # If metadata has which player belongs to which team
                pass 
            
            # 2. Milestones and Personal Bests
            # We'll check both batting and bowling
            for team in teams:
                # Try loading for each team in the match
                bat_stats = self._get_player_career(player_name, team, "batting")
                if bat_stats:
                    # Major Career Milestones
                    # 1. Runs (Major Proximity to 500, 1000...)
                    runs = bat_stats.get("total_runs", 0)
                    if runs > 0:
                        # Use rounded intervals for major career milestones
                        for step in [1000, 500, 250, 100]:
                            next_ms = ((runs // step) + 1) * step
                            needed = next_ms - runs
                            # Threshold depends on milestone size
                            threshold = 50 if step >= 500 else 20
                            
                            ms_obj = {
                                "player": player_name,
                                "type": "runs",
                                "current": int(runs),
                                "target": int(next_ms),
                                "needed": int(needed)
                            }
                            
                            if step == 50:
                                if 0 < needed <= 15: # Generous threshold for backup
                                    all_possible_milestones.append(ms_obj)
                            elif 0 < needed <= threshold:
                                insights["milestone_watch"].append(ms_obj)
                                break

                    # 2. Sixes and Fours (Major Proximity to 50, 100, 250, 500)
                    for col, label in [("sixes", "sixes"), ("fours", "fours")]:
                        val = bat_stats.get(col, 0)
                        if val > 0:
                            # Use major milestone steps as requested
                            for step in [500, 250, 100, 50, 25]:
                                next_ms = ((val // step) + 1) * step
                                needed = next_ms - val
                                
                                ms_obj = {
                                    "player": player_name,
                                    "type": label,
                                    "current": int(val),
                                    "target": int(next_ms),
                                    "needed": int(needed)
                                }
                                
                                if step == 25:
                                    if 0 < needed <= 10:
                                        all_possible_milestones.append(ms_obj)
                                elif 0 < needed <= 10: # Increased threshold to 10 for shots
                                    insights["milestone_watch"].append(ms_obj)
                                    break

                bowl_stats = self._get_player_career(player_name, team, "bowling")
                if bowl_stats:
                    # Major Wicket Milestones (Multiples of 50)
                    wickets = bowl_stats.get("wickets", 0)
                    if wickets > 0:
                        for step in [100, 50, 25]:
                            next_ms = ((wickets // step) + 1) * step
                            needed = next_ms - wickets
                            
                            ms_obj = {
                                "player": player_name,
                                "type": "wickets",
                                "current": int(wickets),
                                "target": int(next_ms),
                                "needed": int(needed)
                            }
                            
                            if step == 25:
                                if 0 < needed <= 5:
                                    all_possible_milestones.append(ms_obj)
                            elif 0 < needed <= 5: # Threshold for wickets
                                insights["milestone_watch"].append(ms_obj)
                                break

        # Check if milestone watch is empty
        if len(insights["milestone_watch"]) == 0 and len(all_possible_milestones) > 0:
            # Sort by least needed effort
            all_possible_milestones.sort(key=lambda x: x["needed"])
            
            # Avoid duplicate players in fallback if possible
            fallback_chosen = []
            seen_players = set()
            for ms in all_possible_milestones:
                if ms["player"] not in seen_players:
                    fallback_chosen.append(ms)
                    seen_players.add(ms["player"])
                if len(fallback_chosen) >= 3:
                    break
                    
            insights["milestone_watch"] = fallback_chosen

        # Save to processed folder
        output_path = self.data_dir / "processed" / "t20" / "matches" / match_id / "pre_match_insights.json"
        os.makedirs(output_path.parent, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(insights, f, indent=2)
        
        return insights

def calculate_pre_match_insights(match_id, data_dir="d:/CricAI/data"):
    # Mock metadata retrieval for standalone call
    meta_path = Path(data_dir) / "processed" / "t20" / "matches" / match_id / "metadata.pkl"
    metadata = {}
    if meta_path.exists():
        import pickle
        with open(meta_path, 'rb') as f:
            metadata = pickle.load(f)
    
    engine = PreMatchInsightEngine(data_dir)
    return engine.generate_insights(match_id, metadata)
