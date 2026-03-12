"""
test_strategy_bot.py — Verification for Strategy Recommendation Bot
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from rag.strategy_bot_engine import StrategyBotEngine

def test_strategy_bot(match_id="1512721"):
    print(f"\n" + "="*60)
    print(f"  Strategy Recommendation Bot - Test (Match {match_id})")
    print("="*60)
    
    bot = StrategyBotEngine()
    
    test_queries = [
        "How should USA rotate their bowlers to handle India's middle order better?"
      
    ]
    
    for q in test_queries:
        print(f"\nUser Query: {q}")
        print("-" * 40)
        
        result = bot.query(match_id, q)
        
        if "error" in result:
            print(f"Error: {result['error']}")
        else:
            print(result.get("answer", "No answer generated."))
        print("-" * 40)

if __name__ == "__main__":
    match_id = sys.argv[1] if len(sys.argv) > 1 else "1512721"
    test_strategy_bot(match_id)
