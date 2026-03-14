"""
pvp_analysis.py — Standalone PvP Data Endpoint
================================================
Mirrors pre_match_analysis.py pattern.
Provides a single function: get_pvp_comparison(match_id, ...)

Usage:
    from rag.pvp_analysis import get_pvp_comparison
    data = get_pvp_comparison("1512721")

Or as a script:
    python pvp_analysis.py 1512721
"""

import os
import sys
import json
from pathlib import Path

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from rag.pvp_engine import PvPComparisonEngine, calculate_pvp_comparison


def get_pvp_comparison(
    match_id: str,
    data_dir: str = "d:/CricAI/data",
    force_refresh: bool = False,
) -> dict:
    """
    Cache-aware data endpoint for PvP Comparison.

    Returns the comparison dict. Saves JSON to:
      data/processed/t20/matches/<match_id>/pvp_comparison.json

    Args:
        match_id:      Target match ID (string)
        data_dir:      Root data directory
        force_refresh: If True, recomputes even if cache exists
    """
    match_id = str(match_id)
    cache_path = (
        Path(data_dir) / "processed" / "t20" / "matches"
        / match_id / "pvp_comparison.json"
    )

    # ── Cache hit ──
    if cache_path.exists() and not force_refresh:
        with open(cache_path, "r") as f:
            return json.load(f)

    # ── Compute ──
    try:
        engine = PvPComparisonEngine(data_dir=data_dir)
        return engine.generate_pvp_comparison(match_id)
    except Exception as e:
        return {
            "match_id": match_id,
            "error": str(e),
        }


# ─────────────────────────────────────────────
# CLI usage
# ─────────────────────────────────────────────
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python pvp_analysis.py <match_id> [--force]")
        sys.exit(1)

    mid   = sys.argv[1]
    force = "--force" in sys.argv

    print(f"\n--- Running PvP Comparison for Match {mid} ---\n")
    result = get_pvp_comparison(mid, force_refresh=force)

    if "error" in result:
        print(f"ERROR: {result['error']}")
        sys.exit(1)

    print(f"Teams: {result['team_a']} vs {result['team_b']}")
    print(f"Total matchups computed: {len(result.get('matchups', []))}\n")

    # Print top 10 most interesting matchups (those where H2H exists)
    matchups = result.get("matchups", [])
    h2h_matchups = [m for m in matchups if "h2h" in m]
    other_matchups = [m for m in matchups if "h2h" not in m]

    print(f"--- {len(h2h_matchups)} matchups with H2H history ---")
    for m in h2h_matchups[:10]:
        h = m["h2h"]
        v = m["v"]
        print(
            f"  {m['bat']:20s} vs {m['bowl']:20s}  |  "
            f"H2H: {h['runs']}r/{h['balls']}b/"
            f"{h['dismissals']}d  SR:{h['strike_rate']}  "
            f"-> Edge: {v.upper()}"
        )

    print(f"\n--- {len(other_matchups)} matchups without H2H (career/team data used) ---")
    for m in other_matchups[:5]:
        v = m["v"]
        print(f"  {m['bat']:20s} vs {m['bowl']:20s}  ->  {v.upper()}")
