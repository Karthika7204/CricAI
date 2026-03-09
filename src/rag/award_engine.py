"""
award_engine.py — V1.0
Deterministic award assignment for CricAI Post-Match Award Engine.

Awards:
  🏆 Player of the Match      — Highest total impact
  🏏 Best Batter              — Highest batting impact (min 15 balls)
  🎯 Best Bowler              — Highest bowling impact (min 2 overs)
  🔥 Game Changer             — Aggressive single-phase dominance
  🧠 Pressure Performer       — Performed under high pressure conditions
  🏅 Emerging Player          — Impact > team avg × 1.5 (no age data needed)
  🧤 Fielding Impact          — Highest fielding proxy score (smart estimation)
  🏏 All-Rounder Impact       — runs>25 AND wickets≥2, highest combined impact

Tie-break priority:
  1. Winning team
  2. Higher pressure_multiplier
  3. More wickets
  4. Higher SR
"""

import json
from pathlib import Path
from impact_engine import compute_impact


# ─────────────────────────────────────────────
# TIE BREAKER
# ─────────────────────────────────────────────

def _tiebreak(candidates: list, score_fn) -> dict:
    """
    Given a list of player dicts and a primary score function,
    apply tie-break logic and return the winner.
    """
    if not candidates:
        return None
    if len(candidates) == 1:
        return candidates[0]

    # Sort by: score DESC, winning team first, pressure multiplier, wickets, sr
    candidates.sort(
        key=lambda p: (
            score_fn(p),
            int(p["is_winner"]),
            p["pressure_multiplier"],
            p["wickets"],
            p["sr"],
        ),
        reverse=True,
    )
    return candidates[0]


# ─────────────────────────────────────────────
# AWARD FUNCTIONS
# ─────────────────────────────────────────────

def _award_player_of_match(players: list) -> dict:
    best = max(players, key=lambda p: (p["total_impact"], int(p["is_winner"])))
    return {
        "name": best["name"],
        "team": best["team"],
        "impact_score": best["total_impact"],
        "breakdown": {
            "batting": best["batting_impact"],
            "bowling": best["bowling_impact"],
            "fielding": best["fielding_proxy"],
            "pressure_multiplier": best["pressure_multiplier"],
        },
        "key_stats": _key_stats(best),
    }


def _award_best_batter(players: list) -> dict:
    eligible = [p for p in players if p["balls"] >= 15]
    if not eligible:
        eligible = [p for p in players if p["runs"] > 0]
    if not eligible:
        return {"name": "N/A", "batting_impact": 0}

    best = _tiebreak(eligible, lambda p: p["batting_impact"])
    return {
        "name": best["name"],
        "team": best["team"],
        "batting_impact": best["batting_impact"],
        "stats": {
            "runs": best["runs"],
            "balls": best["balls"],
            "sr": best["sr"],
            "fours": best["fours"],
            "sixes": best["sixes"],
        },
    }


def _award_best_bowler(players: list) -> dict:
    eligible = [p for p in players if p["overs"] >= 2.0 and p["bowling_impact"] > 0]
    if not eligible:
        eligible = [p for p in players if p["wickets"] > 0]
    if not eligible:
        return {"name": "N/A", "bowling_impact": 0}

    best = _tiebreak(eligible, lambda p: p["bowling_impact"])
    return {
        "name": best["name"],
        "team": best["team"],
        "bowling_impact": best["bowling_impact"],
        "stats": {
            "overs": best["overs"],
            "wickets": best["wickets"],
            "econ": best["econ"],
        },
    }


def _award_game_changer(players: list) -> dict:
    """
    Game Changer = player with the single most dominant phase contribution.
    Proxy:
      - Batters: SR > 160 with sixes ≥ 2 OR runs ≥ 30 with SR > 150
      - Bowlers: 3+ wickets OR economy < 5 over ≥ 3 overs
    Score = batting_impact + bowling_impact (raw, no pressure mult)
    """
    candidates = []
    for p in players:
        gc_score = 0
        is_gc = False

        # Batter criterion
        if p["sr"] >= 150 and p["sixes"] >= 2:
            gc_score += p["batting_impact"] + p["sixes"] * 5
            is_gc = True
        elif p["runs"] >= 30 and p["sr"] >= 150:
            gc_score += p["batting_impact"]
            is_gc = True

        # Bowler criterion
        if p["wickets"] >= 3:
            gc_score += p["bowling_impact"] + 10
            is_gc = True
        elif p["overs"] >= 3 and p["econ"] < 5:
            gc_score += p["bowling_impact"]
            is_gc = True

        if is_gc:
            candidates.append((gc_score, p))

    if not candidates:
        # Fallback: highest raw combined impact
        best = max(players, key=lambda p: p["batting_impact"] + p["bowling_impact"])
        return {
            "name": best["name"],
            "team": best["team"],
            "reason": "Highest combined match impact (fallback)",
            "key_stats": _key_stats(best),
        }

    candidates.sort(key=lambda x: (x[0], int(x[1]["is_winner"])), reverse=True)
    best = candidates[0][1]

    reasons = []
    if best["wickets"] >= 3:
        reasons.append(f"{best['wickets']}-wicket haul")
    if best["sr"] >= 150 and best["sixes"] >= 2:
        reasons.append(f"SR {best['sr']} with {best['sixes']} sixes")
    if best["overs"] >= 3 and best["econ"] < 5:
        reasons.append(f"Exceptional economy {best['econ']}")

    return {
        "name": best["name"],
        "team": best["team"],
        "reason": " | ".join(reasons) if reasons else "Dominant phase performance",
        "key_stats": _key_stats(best),
    }


def _award_pressure_performer(players: list, chasing_team: str) -> dict:
    """
    Pressure Performer = player who delivered under extreme match pressure.
    Logic:
      - Chasing team batter with SR > 140 and runs >= 20
      - OR chasing team bowler with econ < 8 and wickets >= 1
      - OR any player with pressure_multiplier == 1.2 (high pressure phase)
    """
    high_pressure = [p for p in players if p["pressure_multiplier"] >= 1.2]
    if not high_pressure:
        high_pressure = players  # fallback to everyone

    # Score pressure performance
    def pp_score(p):
        score = 0
        if p["team"] == chasing_team:
            score += 20  # bonus for chasing
        if p["sr"] >= 150:
            score += p["batting_impact"]
        if p["econ"] <= 8 and p["overs"] >= 2:
            score += p["bowling_impact"]
        score += p["win_contribution_pct"] * 0.5
        return score

    # Filter meaningful pressure performers
    meaningful = [
        p for p in high_pressure
        if (p["sr"] >= 140 and p["runs"] >= 20)
        or (p["econ"] < 8 and p["overs"] >= 2 and p["wickets"] >= 1)
        or (p["team"] == chasing_team and p["runs"] >= 25)
    ]

    if not meaningful:
        meaningful = high_pressure

    best = _tiebreak(meaningful, pp_score)
    if not best:
        best = players[0]

    pressure_reason = []
    is_bowler = best["overs"] >= 2
    is_batter = best["balls"] >= 10

    if is_batter and best["team"] == chasing_team:
        pressure_reason.append("Chasing team batter under pressure")
    elif is_bowler and best["team"] != chasing_team:
        pressure_reason.append("Defended under high-pressure chase")
    elif best["team"] == chasing_team:
        pressure_reason.append("Chasing team contributor")

    if best["sr"] >= 140 and is_batter:
        pressure_reason.append(f"Attacking SR {best['sr']} under pressure")
    if best["econ"] < 8 and is_bowler:
        pressure_reason.append(f"Economy {best['econ']} while defending chase")

    return {
        "name": best["name"],
        "team": best["team"],
        "pressure_multiplier": best["pressure_multiplier"],
        "reason": " | ".join(pressure_reason) if pressure_reason else "Key performer in pressure phase",
        "key_stats": _key_stats(best),
    }


def _award_emerging_player(players: list) -> dict:
    """
    Emerging Player = Impact Score > team average × 1.5
    (No age data in current pipeline; uses impact-ratio threshold instead)
    Also considers win_contribution_pct as a secondary signal.
    """
    # Calculate team averages
    team_totals = {}
    team_counts = {}
    for p in players:
        t = p["team"]
        team_totals[t] = team_totals.get(t, 0) + p["total_impact"]
        team_counts[t] = team_counts.get(t, 0) + 1

    team_avg = {t: team_totals[t] / max(1, team_counts[t]) for t in team_totals}

    candidates = []
    for p in players:
        avg = team_avg.get(p["team"], 1)
        if p["total_impact"] >= avg * 1.5:
            # Additional: prefer players with fewer career matches (proxy = lower baseline score)
            # If no career data -> assume emerging
            candidates.append((p["total_impact"] / avg, p))

    if not candidates:
        # Fallback: player with highest total_impact relative to team average
        best = max(players, key=lambda p: p["total_impact"] / max(1, team_avg.get(p["team"], 1)))
        return {
            "name": best["name"],
            "team": best["team"],
            "reason": f"Best impact-to-team-average ratio ({round(best['total_impact']/max(1,team_avg.get(best['team'],1)),2)}×)",
            "key_stats": _key_stats(best),
        }

    candidates.sort(key=lambda x: x[0], reverse=True)
    ratio, best = candidates[0]
    return {
        "name": best["name"],
        "team": best["team"],
        "reason": f"Outperformed team average by {round(ratio, 2)}x",
        "key_stats": _key_stats(best),
    }


def _award_fielding_impact(players: list) -> dict:
    """
    Fielding Impact Award using smart proxy score.
    Proxy methodology:
      - Bowlers who generated caught/stumped wickets earn catch attribution credit
        (T20 average ~65% of wickets are catches)
      - High dot ball rate while bowling -> fielding pressure credit
      - Run-out credit shared across bowling team
    """
    # Only award to players who bowled (fielding proxy is from bowling end)
    bowlers = [p for p in players if p["overs"] >= 1.0]
    if not bowlers:
        bowlers = players

    best = max(bowlers, key=lambda p: (p["fielding_proxy"], int(p["is_winner"])))

    # Build reason
    proxy_reasons = []
    if best["wickets"] >= 2:
        catches_est = int(round(best["wickets"] * 0.65))
        proxy_reasons.append(f"Estimated {catches_est} caught dismissals from {best['wickets']} wickets")
    if best["econ"] < 6:
        proxy_reasons.append(f"Economy {best['econ']} — tight fielding support implied")

    return {
        "name": best["name"],
        "team": best["team"],
        "fielding_proxy_score": best["fielding_proxy"],
        "methodology": (
            "Proxy-based: catch attribution (65% T20 wickets are catches) + "
            "dot ball pressure bonus + economy-implied fielding support"
        ),
        "reason": " | ".join(proxy_reasons) if proxy_reasons else "Best fielding contribution proxy",
        "stats": {
            "overs": best["overs"],
            "wickets": best["wickets"],
            "econ": best["econ"],
        },
    }


def _award_allrounder(players: list) -> dict:
    """
    All-Rounder Impact: Optimized for T20 where batting time is limited.
    Highest combined impact among those with meaningful dual-contribution.
    """
    # Tier 1: Strong performance (25+ runs, 2+ wickets)
    eligible = [p for p in players if p["runs"] >= 25 and p["wickets"] >= 2]

    if not eligible:
        # Tier 2: Moderate dual (10+ runs, 2+ wickets OR 20+ runs, 1+ wicket)
        eligible = [p for p in players if (p["runs"] >= 10 and p["wickets"] >= 2) or (p["runs"] >= 20 and p["wickets"] >= 1)]

    if not eligible:
        # Tier 3: Any contribution in both (runs > 0 and wickets > 0)
        eligible = [p for p in players if p["runs"] > 0 and p["wickets"] > 0]

    if not eligible:
        # Tier 4: Any player who both batted and bowled
        eligible = [p for p in players if p["balls"] > 0 and p["overs"] > 0]

    if not eligible:
        return {"name": "N/A", "reason": "No player had both batting and bowling involvement in this match"}

    best = _tiebreak(eligible, lambda p: p["batting_impact"] + p["bowling_impact"])
    ar_score = round(best["batting_impact"] + best["bowling_impact"], 2)
    return {
        "name": best["name"],
        "team": best["team"],
        "all_rounder_score": ar_score,
        "stats": {
            "runs": best["runs"],
            "sr": best["sr"],
            "overs": best["overs"],
            "wickets": best["wickets"],
            "econ": best["econ"],
        },
    }


# ─────────────────────────────────────────────
# UTILITY
# ─────────────────────────────────────────────

def _key_stats(p: dict) -> dict:
    stats = {}
    if p["runs"] > 0:
        stats["batting"] = f"{p['runs']}({p['balls']}) SR:{p['sr']}"
    if p["overs"] > 0:
        stats["bowling"] = f"{p['overs']}ov-{p['wickets']}wkt econ:{p['econ']}"
    return stats


# ─────────────────────────────────────────────
# MAIN ENTRY POINT
# ─────────────────────────────────────────────

def calculate_awards(match_id: str, data_dir: str = "d:/CricAI/data") -> dict:
    """
    Main entry point. Computes all 8 awards for a match.
    Writes awards.json to the match folder.
    Returns the awards dict.
    """
    match_id = str(match_id)
    report = compute_impact(match_id, data_dir)
    players = report["players"]
    chasing_team = report["chasing_team"]

    awards = {
        "match_id": match_id,
        "winner": report["winner"],
        "loser": report["loser"],
        "awards": {
            "player_of_the_match":  _award_player_of_match(players),
            "best_batter":          _award_best_batter(players),
            "best_bowler":          _award_best_bowler(players),
            "game_changer":         _award_game_changer(players),
            "pressure_performer":   _award_pressure_performer(players, chasing_team),
            "emerging_player":      _award_emerging_player(players),
            "fielding_impact":      _award_fielding_impact(players),
            "all_rounder_impact":   _award_allrounder(players),
        },
    }

    # Write to file
    output_path = (
        Path(data_dir) / "processed" / "t20" / "matches" / match_id / "awards.json"
    )
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(awards, f, indent=4, ensure_ascii=False)

    print(f"Awards generated for match {match_id} -> {output_path}")
    return awards


if __name__ == "__main__":
    awards = calculate_awards("1512721")
    for award_name, details in awards["awards"].items():
        winner_name = details.get("name", "N/A")
        print(f"\n  {award_name.replace('_', ' ').upper()}: {winner_name}")
        if "reason" in details:
            print(f"    Reason: {details['reason']}")
        if "key_stats" in details:
            for k, v in details["key_stats"].items():
                print(f"    {k}: {v}")
