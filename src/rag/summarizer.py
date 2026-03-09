import json
from pathlib import Path
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

def generate_summary(match_id, data_dir="d:/CricAI/data"):
    """
    V4.6: Bowling Career Baselines
    - Career vs Match comparison for all bowlers (economy delta, SR delta)
    - Bowling standouts split into Economical / Expensive spells vs career baseline
    - Tactical analysis enriched with career context for bowlers
    """
    match_id = str(match_id)
    match_folder = Path(data_dir) / "processed" / "t20" / "matches" / match_id
    context_path = match_folder / "context.json"
    if not context_path.exists(): return

    with open(context_path, 'r') as f:
        data = json.load(f)

    meta = data['metadata']
    innings = data['innings']
    players = data['players']
    
    # 1. Nomenclature & Formatting
    margin_type = "runs" if meta['margin_runs'] else "wickets"
    margin_val = meta['margin_runs'] or meta['margin_wickets']
    
    # 2. De-duplicated Scorecard Highlights
    core_impact = players[:10]
    core_names = {p['player'] for p in core_impact}
    
    batting = data.get('scorecards', {}).get('batting', [])
    bowling = data.get('scorecards', {}).get('bowling', [])

    # --- Career vs Match: Bowling Comparison ---
    career_vs_match_bowling = []
    for p in bowling:
        baseline = p.get('bowling_baseline', {})
        if not baseline.get('baseline_available', False):
            continue
        career_econ = baseline['career_economy']
        match_econ = p['econ']
        econ_delta = round(match_econ - career_econ, 2)     # positive = more expensive than career
        
        career_sr = baseline['career_sr']
        match_balls = round(p['overs'] * 6) if isinstance(p['overs'], float) else 0
        match_sr = round(match_balls / max(1, p['wickets']), 2) if p['wickets'] > 0 else None

        if econ_delta <= -1.5:
            verdict = f"Exceptional - {abs(econ_delta)} below career economy ({career_econ})"
        elif econ_delta >= 2.0:
            verdict = f"Expensive - {econ_delta} above career economy ({career_econ})"
        else:
            verdict = f"On par with career economy ({career_econ})"

        career_vs_match_bowling.append({
            "player": p['player'],
            "team": p['team'],
            "match_figures": f"{p['overs']}-{p['runs']}-{p['wickets']}",
            "match_economy": match_econ,
            "career_economy": career_econ,
            "economy_delta": econ_delta,
            "match_sr": match_sr,
            "career_sr": career_sr,
            "career_wickets": baseline['career_wickets'],
            "career_best": baseline['best_bowling'],
            "verdict": verdict
        })

    career_vs_match_bowling.sort(key=lambda x: x['economy_delta'])  # best performers first

    # Split into Economical vs Expensive vs baseline
    economical_spells = [p for p in career_vs_match_bowling if p['economy_delta'] <= -1.5]
    expensive_spells  = [p for p in career_vs_match_bowling if p['economy_delta'] >= 2.0]

    # Legacy highlights (non-baseline bowlers or minimal economy >10 spells)
    worst_economy_non_career = sorted(
        [p for p in bowling if not p.get('bowling_baseline', {}).get('baseline_available') and p['econ'] > 10],
        key=lambda x: x['econ'], reverse=True
    )[:2]

    highlights = {
        "Key_Support_Performers": [
            p for p in batting if p['player'] not in core_names and p['runs'] > 15
        ],
        "Career_vs_Match_Bowling": career_vs_match_bowling,
        "Bowling_Standouts": {
            "Economical_Spells": economical_spells,
            "Expensive_Spells": expensive_spells,
            "High_Economy_No_Baseline": worst_economy_non_career
        },
        "Significant_Collapses": [
            {"player": p['player'], "runs": p['runs'], "balls": p['balls']}
            for p in batting if p['runs'] < 10 and p['balls'] > 12
        ]
    }

    # 3. Enhanced Tactical Analysis (Deep Reasoning)
    tactical = []
    winner = meta['winner']
    loser = meta['loser']
    
    # Reasoning for Winner
    top_bat = next((p for p in players if p['team'] == winner and p['role'] == 'batting'), None)
    top_bowl = next((p for p in players if p['team'] == winner and p['role'] == 'bowling'), None)
    
    if top_bat:
        tactical.append(f"{winner}'s victory was anchored by {top_bat['player']}, who contributed {top_bat['win_contribution_percent']}% of the team's runs.")
    if top_bowl:
        tactical.append(f"Defensive pressure was sustained by {top_bowl['player']}, finishing with an impact score of {top_bowl['score']}.")
    
    # Bowling career-context tactical notes
    for entry in career_vs_match_bowling:
        if entry['economy_delta'] <= -2.0:
            tactical.append(
                f"{entry['player']} was outstanding with the ball — economy {entry['match_economy']} vs "
                f"career avg {entry['career_economy']} (delta: {entry['economy_delta']}). A match-defining spell."
            )
        elif entry['economy_delta'] >= 2.0:
            tactical.append(
                f"{entry['player']} struggled with economy {entry['match_economy']} vs "
                f"career avg {entry['career_economy']} (+{entry['economy_delta']}) — an expensive outing."
            )

    # 3.2 Reasoning for Loser & Pressure
    pressure = next((inn['pressure_index'] for inn in innings if inn['team'] == loser and 'pressure_index' in inn), 0)
    if pressure > 80:
        tactical.append(f"{loser} struggled under extreme chase pressure (Index: {round(pressure,1)}), leading to a late-innings collapse.")
    
    # 3.3 Phase Specifics & Advanced Metrics
    for inn in innings:
        team = inn['team']
        pp = inn['phase_analysis']['Powerplay']
        if pp['wkts'] >= 3:
            tactical.append(f"{team} lost {pp['wkts']} wickets in Powerplay, failing to build a stable foundation.")
        
        death = inn['phase_analysis']['Death']
        if death['rr'] > 12:
            tactical.append(f"High-scoring finish by {team} in Death Overs (RR: {death['rr']}) shifted match momentum.")

    # 3.4 Boundary Frequency Check
    for team, stats in data['metadata']['team_summary'].items():
        total_balls = next((inn['balls_faced'] for inn in innings if inn['team'] == team), 120)
        boundaries = stats['fours'] + stats['sixes']
        if boundaries > 0 and (total_balls / boundaries) > 12:
            tactical.append(f"{team} suffered from a lack of boundary frequency (one every {round(total_balls/boundaries, 1)} balls), increasing pressure.")

    # 4. Final V4.6 Structure
    structured_summary = {
        "match_context": {
            "match_id": match_id,
            "date": meta['date'],
            "tournament": meta['tournament'], 
            "venue": meta['venue'], 
            "stage": meta['stage'],
            "Teams": {
                team: {
                    "captain": meta['teams'][team]['captain'],
                    "playing_xi_count": meta['teams'][team]['playing_xi_count']
                } for team in meta['teams']
            }
        },
        "Match_Result": {
            "summary": f"{meta['winner']} won by {margin_val} {margin_type}",
            "winner": meta['winner'],
            "margin": margin_val,
            "margin_type": margin_type
        },
        "Scorecard_Highlights": highlights,
        "Innings_Metrics": innings,
        "Detailed_Impact_Analysis": core_impact,
        "Tactical_Post_Match_Analysis": tactical
    }

    output_path = match_folder / "structured_summary.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(structured_summary, f, indent=4, ensure_ascii=False)
    print(f"Generated V4.6 summary (bowling career context) for {match_id}")

    # ── Auto-generate awards.json alongside the structured summary ──
    try:
        from award_engine import calculate_awards
        calculate_awards(match_id, data_dir)
    except Exception as e:
        print(f"Warning: Award engine failed for {match_id}: {e}")

if __name__ == "__main__":
    generate_summary("1512720")
