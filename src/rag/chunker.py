import json
import re

def generate_match_context_block(data):
    ctx = data.get('match_context', {})
    res = data.get('Match_Result', {})
    return (
        f"Match ID {ctx.get('match_id')} was played on {ctx.get('date')} at {ctx.get('venue')}. "
        f"It was a {ctx.get('stage')} match. "
        f"The outcome: {res.get('summary')}. "
        f"India was led by captain {ctx.get('Teams', {}).get('India', {}).get('captain')}, "
        f"while USA was led by {ctx.get('Teams', {}).get('United States of America', {}).get('captain')}."
    )

def generate_batting_block(data):
    ts = data.get('match_context', {}).get('Team_Summary', {})
    highlights = data.get('Scorecard_Highlights', {})
    
    blocks = []
    for team, stats in ts.items():
        blocks.append(
            f"{team} batting summary: Scored {stats.get('total_runs')} runs for {stats.get('total_wickets')} wickets. "
            f"Run rate: {stats.get('run_rate')}. Hits: {stats.get('fours')} fours and {stats.get('sixes')} sixes. "
            f"Boundary runs contribution: {stats.get('boundary_runs')}. Dot balls faced: {stats.get('dot_balls')}."
        )
    
    for p in highlights.get('Top_Batters', []):
        blocks.append(
            f"Batting Highlight: {p['player']} from {p['team']} scored {p['runs']} off {p['balls']} balls "
            f"(SR: {p['sr']}) with {p['fours']} fours and {p['sixes']} sixes. "
            f"Win contribution: {p['win_contribution_percent']}%."
        )
    return "\n".join(blocks)

def generate_bowling_block(data):
    highlights = data.get('Scorecard_Highlights', {})
    blocks = []
    
    for p in highlights.get('Top_Bowlers', []):
        blocks.append(
            f"Bowling Highlight: {p['player']} from {p['team']} bowled {p['overs']} overs, "
            f"taking {p['wickets']} wickets for {p['runs']} runs (Economy: {p['econ']})."
        )
    
    # Economical spells vs career
    for p in highlights.get('Bowling_Standouts', {}).get('Economical_Spells', []):
        blocks.append(
            f"Bowling Highlight (Economical): {p['player']} ({p['team']}) bowled {p.get('match_figures','N/A')}, "
            f"economy {p['match_economy']} vs career avg {p['career_economy']} "
            f"(delta: {p['economy_delta']}). {p['verdict']}"
        )
    
    # Expensive spells vs career
    for p in highlights.get('Bowling_Standouts', {}).get('Expensive_Spells', []):
        blocks.append(
            f"Bowling Alert (Expensive): {p['player']} ({p['team']}) conceded economy {p['match_economy']} "
            f"vs career avg {p['career_economy']} (+{p['economy_delta']}). {p['verdict']}"
        )

    # High-economy spells with no baseline
    for p in highlights.get('Bowling_Standouts', {}).get('High_Economy_No_Baseline', []) or \
             highlights.get('Worst_Economy_Spells', []):
        blocks.append(
            f"Bowling Alert (High Economy): {p['player']} ({p['team']}) conceded {p['runs']} runs "
            f"in {p['overs']} overs at an economy of {p['econ']}."
        )
    return "\n".join(blocks)


def generate_career_bowling_context_block(data):
    """Generates a dedicated narrative block comparing each bowler's match performance
    against their career baseline. This chunk is tagged specifically for career-form queries."""
    cv_bowling = data.get('Scorecard_Highlights', {}).get('Career_vs_Match_Bowling', [])
    if not cv_bowling:
        return ""
    blocks = ["Career vs Match Bowling Comparison:"]
    for p in cv_bowling:
        delta_str = f"+{p['economy_delta']}" if p['economy_delta'] > 0 else str(p['economy_delta'])
        blocks.append(
            f"{p['player']} ({p['team']}): match figures {p.get('match_figures','N/A')}, "
            f"economy {p['match_economy']} (career: {p['career_economy']}, delta: {delta_str}). "
            f"Career wickets: {p['career_wickets']}, best: {p['career_best']}. "
            f"Verdict: {p['verdict']}"
        )
    return "\n".join(blocks)

def generate_phase_analysis_block(data):
    innings = data.get('Innings_Metrics', [])
    blocks = []
    for inn in innings:
        team = inn.get('team')
        phases = inn.get('phase_analysis', {})
        for name, p_data in phases.items():
            blocks.append(
                f"Innings {inn.get('innings')} ({team}) {name} Phase: "
                f"Scored {p_data.get('runs')} runs, lost {p_data.get('wkts')} wickets at RR {p_data.get('rr')}."
            )
    return "\n".join(blocks)

def generate_tactical_block(data):
    analysis = data.get('Tactical_Post_Match_Analysis', [])
    return "\n".join(analysis)

def get_chunks_with_tags(data):
    """
    V5.1 Chunker: Career-aware bowling context added.
    """
    career_bowling_block = generate_career_bowling_context_block(data)
    blocks = [
        {"text": generate_match_context_block(data), "tags": ["context", "result", "venue", "captain"]},
        {"text": generate_batting_block(data), "tags": ["batting", "runs", "highlights"]},
        {"text": generate_bowling_block(data), "tags": ["bowling", "wickets", "economy"]},
        {"text": generate_phase_analysis_block(data), "tags": ["phase", "powerplay", "middle", "death"]},
        {"text": generate_tactical_block(data), "tags": ["tactical", "analysis", "grounding"]},
    ]

    # Add career bowling chunk only if baseline data exists
    if career_bowling_block:
        blocks.append({
            "text": career_bowling_block,
            "tags": ["career", "bowling", "baseline", "comparison", "economy", "form"]
        })

    # Also add specific player tags to blocks where they appear
    impact = data.get('Detailed_Impact_Analysis', [])
    for p in impact:
        p_name = p['player']
        role = p.get('role', 'player')
        stats = p.get('match_stats', "")
        text = f"Detailed Impact: {p_name} ({p['team']}) as {role}. Match performance: {stats}. Impact Score: {p['score']}."
        # Append bowling career context for bowlers
        if role == 'bowling':
            bl = p.get('bowling_baseline', {})
            if bl.get('baseline_available'):
                text += (
                    f" Career: {bl['career_wickets']} wickets at economy {bl['career_economy']}, "
                    f"best {bl['best_bowling']}."
                )
        blocks.append({"text": text, "tags": [p_name, p['team'], role, "impact"]})
        
    return blocks
