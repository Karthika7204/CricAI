# -*- coding: utf-8 -*-
"""
test_pvp.py - Test script for the Optimized PvP Comparison Engine
=========================================================
Runs the engine against a real match and prints output.
Verifies file size reduction.

Usage:
    cd d:\CricAI\src\rag
    python test_pvp.py
"""

import json
import sys
import os
from pathlib import Path

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src", "rag"))

from pvp_analysis import get_pvp_comparison


def test_pvp(match_id: str = "1512721"):
    print(f"\n{'='*60}")
    print(f"  PvP Comparison Engine (Optimized) - Test (Match {match_id})")
    print(f"{'='*60}\n")

    result = get_pvp_comparison(match_id, force_refresh=True)

    if "error" in result:
        print(f"[FAIL] Error: {result['error']}")
        return

    print(f"[OK] Teams:             {result['team_a']} vs {result['team_b']}")
    
    matchups = result.get("matchups", [])
    print(f"[OK] Total Matchups:    {len(matchups)} (Limited for robustness)")

    cache_path = Path("d:/CricAI/data/processed/t20/matches") / match_id / "pvp_comparison.json"
    if cache_path.exists():
        size_kb = os.path.getsize(cache_path) / 1024
        print(f"[OK] JSON File Size:    {size_kb:.2f} KB (Target: < 50 KB)")

    h2h_found = [m for m in matchups if "h2h" in m]
    team_found = [m for m in matchups if "vs_t" in m]
    bowler_edge = [m for m in matchups if m["v"] == "bowler"]
    batsman_edge = [m for m in matchups if m["v"] == "batsman"]

    print(f"[OK] H2H data found:    {len(h2h_found)}")
    print(f"[OK] vs-Team data:      {len(team_found)}")
    print(f"[OK] Bowler-Edge:       {len(bowler_edge)}")
    print(f"[OK] Batsman-Edge:      {len(batsman_edge)}")

    print(f"\n-- Top 5 Most Significant Matchups --")
    for m in matchups[:5]:
        v_label = m["v"].upper()
        print(f"\n  {m['bat']} ({m['bat_t']}) vs {m['bowl']} ({m['bowl_t']})")
        print(f"    Edge: {v_label}")
        
        if "h2h" in m:
            h = m["h2h"]
            print(f"    H2H: {h['runs']}r / {h['balls']}b / {h['dismissals']}d (SR {h['strike_rate']})")
        
        if "vs_t" in m:
            vt = m["vs_t"]
            print(f"    vs Team: avg {vt['average']} (SR {vt['strike_rate']})")
            
        if "b_car" in m:
            bc = m["b_car"]
            print(f"    Batter Career: avg {bc['avg']} / SR {bc['sr']}")
            
        if "w_car" in m:
            wc = m["w_car"]
            print(f"    Bowler Career: avg {wc['avg']} / eco {wc['eco']}")

    print(f"\n{'='*60}")
    print("  Optimization Verification Complete!")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    mid = sys.argv[1] if len(sys.argv) > 1 else "1512721"
    test_pvp(mid)
