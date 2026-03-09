"""
test_awards.py ? Standalone test for the AI Post-Match Award Engine.
Runs on match 1512721 (India vs USA, T20 World Cup 2026).
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from award_engine import calculate_awards
import json

MATCH_ID = "1512721"

AWARD_EMOJIS = {
    "player_of_the_match":  "[POTM]",
    "best_batter":          "[BAT]",
    "best_bowler":          "[BOWL]",
    "game_changer":         "[GC]",
    "pressure_performer":   "[PP]",
    "emerging_player":      "[EP]",
    "fielding_impact":      "[FI]",
    "all_rounder_impact":   "[BAT]",
}

def run():
    print(f"\n{'='*60}")
    print(f"  CricAI Post-Match Award Engine ? Match {MATCH_ID}")
    print(f"{'='*60}\n")

    awards = calculate_awards(MATCH_ID)

    winner = awards.get("winner", "?")
    print(f"  Match Result: {winner} won\n")
    print(f"  {'-'*56}")

    all_awards = awards.get("awards", {})
    assert len(all_awards) == 8, f"Expected 8 awards, got {len(all_awards)}"

    for award_key, details in all_awards.items():
        emoji = AWARD_EMOJIS.get(award_key, "??")
        award_display = award_key.replace("_", " ").title()
        winner_name = details.get("name", "N/A")

        print(f"  {emoji}  {award_display}")
        print(f"      Winner : {winner_name} ({details.get('team', '')})")

        # Print score if available
        for score_key in ["impact_score", "batting_impact", "bowling_impact",
                          "all_rounder_score", "fielding_proxy_score"]:
            if score_key in details:
                print(f"      Score  : {details[score_key]}")
                break

        if "reason" in details:
            print(f"      Reason : {details['reason']}")

        if "stats" in details:
            print(f"      Stats  : {details['stats']}")
        elif "key_stats" in details and details["key_stats"]:
            for k, v in details["key_stats"].items():
                print(f"      {k.title():7s}: {v}")

        if "methodology" in details:
            print(f"      Method : {details['methodology']}")

        print()

    print(f"  {'-'*56}")
    print(f"  ? All 8 awards generated successfully.\n")
    print(f"  awards.json saved to: d:/CricAI/data/processed/t20/matches/{MATCH_ID}/awards.json\n")

    # Verify key assertions
    potm = all_awards["player_of_the_match"]
    assert potm.get("name") not in (None, "N/A"), "Player of the Match must be assigned"
    assert potm.get("impact_score", 0) > 0, "POTM impact score must be > 0"

    best_bowl = all_awards["best_bowler"]
    assert best_bowl.get("stats", {}).get("overs", 0) >= 2.0, "Best bowler must have bowled ?2 overs"

    print("  ? Assertions passed.\n")


if __name__ == "__main__":
    run()
