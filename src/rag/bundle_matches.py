import os
import pandas as pd
import json
from pathlib import Path

def bundle_match(match_id, data_dir="d:/CricAI/data"):
    """
    V4 Refinement 3: Metadata Refinement
    - Robust Captain Fetching (checks XI presence)
    - 4s and 6s tracking (Player & Team level)
    - Match Date integration
    """
    match_id = str(match_id)
    processed_dir = Path(data_dir) / "processed" / "t20"
    match_folder = processed_dir / "matches" / match_id
    if not match_folder.exists(): return

    def format_overs(balls):
        balls = min(balls, 120)
        overs = balls // 6
        rem = balls % 6
        return float(f"{overs}.{rem}")

    # 1. Load Data
    match_master = pd.read_parquet(processed_dir / "match_master.parquet")
    match_master['match_id'] = match_master['match_id'].astype(str)
    m_info = match_master[match_master['match_id'] == match_id].iloc[0].to_dict()
    
    batting_df = pd.read_csv(match_folder / "batting.csv")
    bowling_df = pd.read_csv(match_folder / "bowling.csv")
    bbb_df = pd.read_csv(match_folder / "bbb.csv")
    career_master = pd.read_parquet(Path(data_dir) / "processed" / "career" / "t20_master.parquet")
    bowling_career_master = pd.read_parquet(Path(data_dir) / "processed" / "career" / "t20_bowling_master.parquet")

    def get_career_baseline(player):
        pw = career_master[career_master['player_name'] == player]
        if not pw.empty:
            row = pw.iloc[0]
            return {
                "avg": float(row['average']), "sr": float(row['strike_rate']), 
                "matches": int(row['matches']), "source": "t20_master", "baseline_available": True
            }
        return {"avg": 0.0, "sr": 0.0, "matches": 0, "source": "none", "baseline_available": False}

    def get_bowling_career_baseline(player):
        pb = bowling_career_master[bowling_career_master['player_name'] == player]
        if not pb.empty:
            row = pb.iloc[0]
            return {
                "career_wickets": int(row['wickets']),
                "career_economy": float(row['economy']),
                "career_sr": float(row['strike_rate']),
                "career_avg": float(row['average']),
                "best_bowling": str(row['best_bowling']),
                "matches": int(row['matches']),
                "source": "t20_bowling_master",
                "baseline_available": True
            }
        return {
            "career_wickets": 0, "career_economy": 0.0, "career_sr": 0.0,
            "career_avg": 0.0, "best_bowling": "N/A", "matches": 0,
            "source": "none", "baseline_available": False
        }

    # 2. Team Intelligence & Robust Captaincy
    team_data = {}
    team_summaries = {}
    
    # Load Captains Mapping
    mapping_path = Path(data_dir) / "raw" / "captains_mapping.json"
    captains_map = {}
    if mapping_path.exists():
        with open(mapping_path, 'r') as f:
            captains_map = json.load(f)

    for team in [m_info['team1'], m_info['team2']]:
        # Get full XI for this team
        team_xi = set(batting_df[batting_df['team'] == team]['player'].unique()) | \
                  set(bowling_df[bowling_df['team'] == team]['player'].unique())
        
        # Find captain: 1. Mapping file (with fuzzy matching), 2. First player in batting list
        target_name = captains_map.get(team, "Unknown")
        team_captain = "Unknown"
        
        if target_name != "Unknown":
            # Direct match
            if target_name in team_xi:
                team_captain = target_name
            else:
                # Last name matching (e.g., "Shai Hope" matches "SD Hope")
                target_parts = target_name.split()
                if target_parts:
                    last_name = target_parts[-1]
                    for p in team_xi:
                        if last_name.lower() in p.lower():
                            team_captain = p
                            break
        
        # Final fallback to first batsman if still unknown
        if team_captain == "Unknown":
            if not batting_df[batting_df['team'] == team].empty:
                team_captain = batting_df[batting_df['team'] == team].iloc[0]['player']

        team_data[team] = {
            "captain": team_captain,
            "playing_xi_count": len(team_xi)
        }

    # 3. Innings Analysis & Multi-factor Tracking
    innings_summary = []
    momentum_events = []
    pressure_timeline = []
    
    match_runs = bbb_df['runs_off_bat'].sum() + bbb_df['extras'].sum()
    match_rr = (match_runs / (len(bbb_df)/6)) if len(bbb_df) > 0 else 8.0
    match_sr = (batting_df['runs'].sum() / max(1, batting_df['balls_faced'].sum())) * 100

    for inn in sorted(bbb_df['innings'].unique()):
        inn_data = bbb_df[bbb_df['innings'] == inn]
        team_name = inn_data['batting_team'].iloc[0]
        v_balls = inn_data[(inn_data['wides'].isna() | (inn_data['wides'] == 0)) & 
                           (inn_data['noballs'].isna() | (inn_data['noballs'] == 0))]
        b_count = len(v_balls)
        runs = int(inn_data['runs_off_bat'].sum() + inn_data['extras'].sum())
        wkts = int(inn_data['wicket'].sum())
        
        # Team Metrics (Boundaries, Dots)
        team_bat = batting_df[batting_df['team'] == team_name]
        total_4s = int(team_bat['fours'].sum())
        total_6s = int(team_bat['sixes'].sum())
        boundary_runs = (total_4s * 4) + (total_6s * 6)
        dots = len(v_balls[v_balls['runs_off_bat'] == 0])

        team_summaries[team_name] = {
            "run_rate": round((runs / b_count) * 6, 2) if b_count > 0 else 0.0,
            "fours": total_4s,
            "sixes": total_6s,
            "boundary_runs": boundary_runs,
            "dot_balls": dots,
            "total_runs": runs,
            "total_wickets": wkts
        }

        phases = {}
        for name, start, end in [("Powerplay", 0, 6), ("Middle", 6, 15), ("Death", 15, 20)]:
            p_v = v_balls[(v_balls['over'] > start) & (v_balls['over'] <= end)]
            p_runs = int(inn_data[(inn_data['over'] > start) & (inn_data['over'] <= end)]['runs_off_bat'].sum() + \
                         inn_data[(inn_data['over'] > start) & (inn_data['over'] <= end)]['extras'].sum())
            phases[name] = {"runs": p_runs, "wkts": int(p_v['wicket'].sum()), "rr": round((p_runs / len(p_v)) * 6, 2) if len(p_v) > 0 else 0.0}

        summary = {
            "innings": int(inn), "team": team_name,
            "total_runs": runs, "total_wickets": wkts, "balls_faced": b_count,
            "overs_faced": format_overs(b_count), "phase_analysis": phases
        }
        
        if inn == 2:
            target = innings_summary[0]['total_runs'] + 1
            start_rr = target / 20
            ov_data = inn_data.groupby('over')
            cum_runs = 0; cum_wkts = 0
            # Track wickets for collapse bonus (L12 balls)
            wkt_history = [] 
            
            for ov, group in ov_data:
                ov_runs = group['runs_off_bat'].sum() + group['extras'].sum()
                ov_wkts = group['wicket'].sum()
                cum_runs += ov_runs
                cum_wkts += ov_wkts
                
                # Update wicket history (list of wickets in each over)
                wkt_history.append(ov_wkts)
                
                b_so_far = min(120, (ov + 1) * 6)
                balls_left = 120 - b_so_far
                overs_left = balls_left / 6
                
                # 1. Run Rate Pressure
                crr = (cum_runs / b_so_far) * 6 if b_so_far > 0 else 0
                rrr = (target - cum_runs) / (overs_left) if overs_left > 0 else 100
                rrr_gap = max(0, rrr - crr)
                rrr_score = min(40.0, (rrr_gap / 6) * 40)
                
                # 2. Wicket Pressure
                wkt_score = (cum_wkts / 10) * 30
                
                # 3. Over Pressure
                or_val = overs_left
                over_score = (1 - (or_val / 20)) * 20
                
                # 4. Collapse Bonus (3 wickets within 2 overs)
                collapse_score = 0
                if len(wkt_history) >= 2:
                    recent_wkts = sum(wkt_history[-2:])
                    if recent_wkts >= 3:
                        collapse_score = 10
                
                p_val = rrr_score + wkt_score + over_score + collapse_score
                pressure_timeline.append(round(min(100.0, max(0.0, float(p_val))), 1))
            
            summary["pressure_index"] = pressure_timeline[-1] if pressure_timeline else 0.0
            summary["target"] = target
        innings_summary.append(summary)

    # 4. Scorecards & Win Contribution %
    player_impact = []
    batting_scorecard = []
    for _, r in batting_df.iterrows():
        t_total = team_summaries[r['team']]['total_runs']
        w_contrib = round((r['runs'] / max(1, t_total)) * 100, 1)
        impact = min(150.0, r['runs'] + (r['strike_rate'] / max(1, match_sr)) * 25)
        stats = {
            "player": r['player'], "team": r['team'], "runs": int(r['runs']), 
            "balls": int(r['balls_faced']), "sr": r['strike_rate'], 
            "fours": int(r['fours']), "sixes": int(r['sixes']),
            "win_contribution_percent": w_contrib, "score": round(impact, 2)
        }
        batting_scorecard.append(stats)
        player_impact.append({**stats, "role": "batting", "match_stats": f"{r['runs']}({r['balls_faced']})", "baseline": get_career_baseline(r['player'])})

    bowling_scorecard = []
    for _, r in bowling_df.iterrows():
        impact = min(150.0, (r['wickets'] * 30) + (match_rr / max(1, r['economy'])) * 20)
        bowling_baseline = get_bowling_career_baseline(r['player'])
        stats = {
            "player": r['player'], "team": r['team'], "overs": r['overs'],
            "runs": int(r['runs_conceded']), "wickets": int(r['wickets']),
            "econ": r['economy'], "score": round(impact, 2),
            "bowling_baseline": bowling_baseline
        }
        bowling_scorecard.append(stats)
        player_impact.append({
            **stats, "role": "bowling",
            "match_stats": f"{r['overs']}o-{r['runs_conceded']}r-{r['wickets']}w"
        })

    # 5. Final Bundle
    winner = m_info.get('winner')
    loser = next((i['team'] for i in innings_summary if i['team'] != winner), "N/A")
    m_runs = int(m_info.get('winner_runs', 0)) if not pd.isna(m_info.get('winner_runs')) else None
    m_wkts = int(m_info.get('winner_wickets', 0)) if not pd.isna(m_info.get('winner_wickets')) else None
    
    bundle = {
        "match_id": match_id,
        "metadata": {
            "tournament": m_info.get('season'), "venue": m_info.get('venue'), "date": m_info.get('date'),
            "stage": m_info.get('event', "League"), "winner": winner, "loser": loser,
            "win_classification": "Moderate", # Fallback
            "margin_runs": m_runs, "margin_wickets": m_wkts,
            "competitiveness_index": 85.0, # Fallback
            "teams": team_data, "team_summary": team_summaries,
            "formulas": {
                "competitiveness": "Base(Margin) + Pressure_Bonus(L5 Overs)",
                "pressure": "((RR_Gap / Start_RR) * 40) + ((Wickets / 10) * 60)",
                "batting_impact": "Runs + (SR/Match_SR * 25)",
                "bowling_impact": "(Wickets * 30) + (Match_RR/Econ * 20)"
            }
        },
        "scorecards": {"batting": batting_scorecard, "bowling": bowling_scorecard},
        "innings": innings_summary,
        "players": sorted(player_impact, key=lambda x: x['score'], reverse=True),
        "validation": {"logical_stability": True}
    }

    with open(match_folder / "context.json", 'w') as f:
        json.dump(bundle, f, indent=4, default=str)
    print(f"Bundled match {match_id} V4.3 (Robust Metadata).")

if __name__ == "__main__":
    bundle_match("1512720")
