"""
impact_engine.py — V1.0
Deterministic per-player impact score calculator for CricAI Award Engine.

Reads context.json and computes:
  - Batting Impact Score
  - Bowling Impact Score
  - Fielding Proxy Score (derived from caught wickets per bowler + dot pressure)
  - Pressure Multiplier (applied to total)

Fielding Note:
  Raw fielder data (catches/run-outs per player) is not stored in context.json.
  We use a smart proxy: bowlers who generated caught/lbw/stumped dismissals
  in their spell receive fielding proxy credit (catch attribution), and
  bowlers with high dot ball rates receive additional fielding pressure credit.
  This is a recognised proxy in cricket analytics when raw fielding logs are absent.
"""

import json
from pathlib import Path


# ─────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────
SR_BONUS_THRESHOLDS = [(170, 15), (150, 10), (130, 5)]
ECONOMY_BONUS_MAP   = [(6, 20), (7.5, 10), (10, 0), (12, -15)]
ECONOMY_PENALTY_MAP = [(12, -25), (10, -15)]
DEATH_ECONOMY_THRESHOLD = 8
DEATH_OVER_BONUS    = 15
DOT_BALL_BAT_THRESH = 50   # dot% above this → penalty
DOT_BALL_BOWL_THRESH = 50  # dot% above this → bonus
DOT_BALL_BAT_PENALTY = -10
DOT_BALL_BOWL_BONUS  = 10
WICKET_WEIGHT       = 25
DEATH_RUNS_MULTIPLIER = 0.5
CHASE_PRESSURE_BONUS  = 10

# Fielding proxy weights
CAUGHT_PROXY_PER_WICKET   = 8   # per caught/stumped wicket in spell
RUNOUT_PROXY_PER_WICKET   = 12  # per run-out (assigned to bowling team)
DOT_FIELDING_PROXY_BONUS  = 5   # for dot% > 40 while bowling


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def _overs_to_balls(overs: float) -> int:
    """Convert 4.2 overs → 26 balls."""
    full = int(overs)
    partial = round((overs - full) * 10)
    return full * 6 + partial


def _batting_impact(player: dict, is_chasing: bool, death_phase_runs: dict) -> float:
    """
    Compute batting impact for one player.
    player keys: runs, balls, sr, fours, sixes
    death_phase_runs: {team: death_runs} — used to estimate death over contribution
    """
    runs   = player.get("runs", 0) or 0
    balls  = player.get("balls", 0) or 0
    sr     = player.get("sr", 0.0) or 0.0
    fours  = player.get("fours", 0) or 0
    sixes  = player.get("sixes", 0) or 0
    team   = player.get("team", "")

    if runs == 0 and balls == 0:
        return 0.0

    boundary_runs = fours * 4 + sixes * 6

    # Strike rate bonus
    sr_bonus = 0
    for threshold, bonus in SR_BONUS_THRESHOLDS:
        if sr >= threshold:
            sr_bonus = bonus
            break

    # Phase pressure bonus (death over proxy: boundary heavy players score here)
    phase_bonus = 0.0
    if is_chasing:
        phase_bonus += CHASE_PRESSURE_BONUS
    # Proxy for death-over runs: if a batter scored many sixes they likely batted in death
    death_proxy = sixes * 6 * DEATH_RUNS_MULTIPLIER
    phase_bonus += death_proxy

    # Dot ball penalty (inferred: balls - scoring balls)
    scoring_balls = max(fours + sixes, 1)  # at minimum the boundary balls
    # We don't have per-ball data per batter, so estimate dot%:
    # dot_balls ≈ balls - (runs/4 for fours area) — simplified proxy
    estimated_non_dot = min(balls, fours + sixes + max(1, int(runs / 4)))
    dot_pct = max(0, (balls - estimated_non_dot) / max(balls, 1) * 100)
    dot_penalty = DOT_BALL_BAT_PENALTY if dot_pct > DOT_BALL_BAT_THRESH else 0

    impact = (
        runs * 1.0
        + boundary_runs * 0.5
        + sr_bonus
        + phase_bonus
        + dot_penalty
    )
    return round(max(0.0, impact), 2)


def _bowling_impact(player: dict, total_match_overs: float) -> float:
    """
    Compute bowling impact for one player.
    player keys: overs, runs (conceded), wickets, econ
    """
    overs   = player.get("overs", 0.0) or 0.0
    wickets = player.get("wickets", 0) or 0
    econ    = player.get("econ", 0.0) or 0.0
    runs_conceded = player.get("runs", 0) or 0

    if overs == 0:
        return 0.0

    balls_bowled = _overs_to_balls(overs)

    # Economy bonus/penalty
    if econ < 6:
        eco_bonus = 20
    elif econ < 7.5:
        eco_bonus = 10
    elif econ > 12:
        eco_bonus = -25
    elif econ > 10:
        eco_bonus = -15
    else:
        eco_bonus = 0

    # Dot ball bonus (approximated from economy — low economy implies high dot balls)
    # dot% proxy: (balls - runs_conceded/6) / balls
    # If econ < 6 → very likely >50% dot balls
    dot_bowl_bonus = 0
    estimated_scoring_balls = int(runs_conceded / 2)  # rough: each scoring ball scores ~2
    if balls_bowled > 0:
        dot_pct = max(0, (balls_bowled - estimated_scoring_balls) / balls_bowled * 100)
        dot_bowl_bonus = DOT_BALL_BOWL_BONUS if dot_pct > DOT_BALL_BOWL_THRESH else 0

    # Death over bonus — if bowl count >= 12 balls (2 overs) and economy tight
    death_bonus = 0
    if overs >= 2.0 and econ < DEATH_ECONOMY_THRESHOLD:
        death_bonus = DEATH_OVER_BONUS

    impact = (
        wickets * WICKET_WEIGHT
        + eco_bonus
        + dot_bowl_bonus
        + death_bonus
    )
    return round(max(0.0, impact), 2)


def _fielding_proxy(player: dict, caught_counts: dict, runout_counts: dict) -> float:
    """
    Smart fielding proxy for a player (based on bowler-assisted dismissal analysis).

    caught_counts: {player_name: int}  — caught wickets attr to bowler
    runout_counts: {team: int}         — run-outs per team (shared proxy)
    """
    name = player.get("player", "")
    overs = player.get("overs", 0.0) or 0.0

    # Bowlers get credit for creating catching opportunities
    catches_in_spell = caught_counts.get(name, 0)
    fielding_score = catches_in_spell * CAUGHT_PROXY_PER_WICKET

    # Run-out: allocated evenly to all fielders in the fielding team
    # (We know it happened; assign partial credit per bowler on that team)
    team = player.get("team", "")
    team_runouts = runout_counts.get(team, 0)
    if team_runouts > 0 and overs > 0:
        # Share run-out credit among active bowlers on team
        fielding_score += (team_runouts * RUNOUT_PROXY_PER_WICKET) / 4.0  # ~4 active bowlers

    # Dot ball fielding proxy for tight spells
    econ = player.get("econ", 0.0) or 0.0
    if econ < 6 and overs >= 2:
        fielding_score += DOT_FIELDING_PROXY_BONUS

    return round(max(0.0, fielding_score), 2)


def _pressure_multiplier(innings: list, team: str) -> float:
    """
    Returns pressure multiplier based on chase pressure index.
    """
    for inn in innings:
        if inn["team"] == team and "pressure_index" in inn:
            pi = inn["pressure_index"]
            if pi >= 80:
                return 1.2
            elif pi >= 60:
                return 1.1
    return 1.0


# ─────────────────────────────────────────────
# MAIN: compute_impact
# ─────────────────────────────────────────────

def compute_impact(match_id: str, data_dir: str = "d:/CricAI/data") -> dict:
    """
    Reads context.json for match_id and returns a full impact report:
    {
      "match_id": ...,
      "winner": ...,
      "players": [
        {
          "name", "team", "is_winner",
          "batting_impact", "bowling_impact", "fielding_proxy",
          "total_impact", "pressure_multiplier",
          # raw stats
          "runs", "balls", "sr", "fours", "sixes",
          "overs", "wickets", "econ",
        }, ...
      ]
    }
    """
    match_id = str(match_id)
    path = Path(data_dir) / "processed" / "t20" / "matches" / match_id / "context.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    meta    = data["metadata"]
    innings = data["innings"]
    batting_sc = data["scorecards"]["batting"]
    bowling_sc = data["scorecards"]["bowling"]

    winner = meta["winner"]
    loser  = meta["loser"]

    # ── Determine chasing team ──────────────────────────────────────────
    # Innings 2 team is always chasing
    chasing_team = next((inn["team"] for inn in innings if inn["innings"] == 2), loser)

    # ── Build caught/runout counts from wicket data in bbb.csv ─────────
    # We derive caught wicket counts per bowler from bowling scorecard:
    # We don't have ball-by-ball fielder info, so we infer:
    # "wickets" in bowling scorecard = total dismissals by that bowler
    # Assume ~70% are catches (T20 average), rest are bowled/lbw
    # This gives each bowler partial catch credit proportional to wickets
    caught_counts = {}
    runout_counts = {meta["winner"]: 0, meta["loser"]: 0}

    for p in bowling_sc:
        wkts = p.get("wickets", 0) or 0
        name = p["player"]
        # Use wickets as proxy for caught-off-bowling (fair T20 average)
        caught_counts[name] = int(round(wkts * 0.65))  # ~65% wickets are catches in T20s

    # ── Build lookup maps ───────────────────────────────────────────────
    bat_map  = {p["player"]: p for p in batting_sc}
    bowl_map = {p["player"]: p for p in bowling_sc}
    all_players = set(bat_map.keys()) | set(bowl_map.keys())

    results = []

    for pname in all_players:
        bat_p  = bat_map.get(pname, {})
        bowl_p = bowl_map.get(pname, {})
        team   = bat_p.get("team") or bowl_p.get("team", "Unknown")

        is_chasing = (team == chasing_team)
        pmul = _pressure_multiplier(innings, team)

        # ── Sub-scores ──────────────────────────────────────────────────
        b_imp  = _batting_impact(bat_p, is_chasing, {})
        bw_imp = _bowling_impact(bowl_p, 20.0)
        f_imp  = _fielding_proxy(bowl_p or bat_p, caught_counts, runout_counts)

        total  = round((b_imp + bw_imp + f_imp) * pmul, 2)

        results.append({
            "name":               pname,
            "team":               team,
            "is_winner":          (team == winner),
            # sub-scores
            "batting_impact":     b_imp,
            "bowling_impact":     bw_imp,
            "fielding_proxy":     f_imp,
            "pressure_multiplier": pmul,
            "total_impact":       total,
            # raw batting
            "runs":   bat_p.get("runs", 0) or 0,
            "balls":  bat_p.get("balls", 0) or 0,
            "sr":     bat_p.get("sr", 0.0) or 0.0,
            "fours":  bat_p.get("fours", 0) or 0,
            "sixes":  bat_p.get("sixes", 0) or 0,
            "win_contribution_pct": bat_p.get("win_contribution_percent", 0) or 0,
            # raw bowling
            "overs":   bowl_p.get("overs", 0.0) or 0.0,
            "wickets": bowl_p.get("wickets", 0) or 0,
            "econ":    bowl_p.get("econ", 0.0) or 0.0,
        })

    results.sort(key=lambda x: x["total_impact"], reverse=True)

    return {
        "match_id": match_id,
        "winner":   winner,
        "loser":    loser,
        "chasing_team": chasing_team,
        "players":  results,
    }


if __name__ == "__main__":
    report = compute_impact("1512721")
    print(f"\nTop 5 Impact Players — Match {report['match_id']}:")
    for p in report["players"][:5]:
        print(
            f"  {p['name']:25s} | Total: {p['total_impact']:6.1f} "
            f"| Bat: {p['batting_impact']:5.1f} Bowl: {p['bowling_impact']:5.1f} "
            f"Field: {p['fielding_proxy']:4.1f} | Team: {p['team']}"
        )
