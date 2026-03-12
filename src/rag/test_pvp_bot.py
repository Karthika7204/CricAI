# -*- coding: utf-8 -*-
"""
test_pvp_bot.py - Test script for the Conversational PvP Bot
============================================================
Verifies natural language queries for match-specific player matchups.

Usage:
    cd d:\CricAI\src\rag
    python test_pvp_bot.py
"""

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from rag.pvp_bot_engine import PvPBotEngine

def test_pvp_bot(match_id: str = "1512721"):
    print(f"\n{'='*60}")
    print(f"  PvP Recommendation Bot - Test (Match {match_id})")
    print(f"{'='*60}\n")

    bot = PvPBotEngine()
    
    test_queries = [
        "Who is good and bad against Surya Kumar Yadav in this match?",
        "How can the USA batsmen handle Arshdeep Singh?",
        "Give me some general recommendations for the key matchups in this match."
    ]

    for q in test_queries:
        print(f"User Query: {q}")
        print("-" * 40)
        res = bot.query(match_id, q)
        
        if "error" in res:
            print(f"[FAIL] Error: {res['error']}")
        else:
            print(res.get("answer", "No answer generated."))
            if res.get("mentioned_players"):
                print(f"(Mentioned Players detected: {', '.join(res['mentioned_players'])})")
        print("-" * 40 + "\n")

    print(f"{'='*60}")
    print("  PvP Bot Verification Complete!")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    test_pvp_bot()
