"""
test_pressure_bot.py — Test script for PressureBotEngine
"""
import sys
import os
import json

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from rag.pressure_bot_engine import PressureBotEngine

def test_pressure_bot():
    print("Initializing PressureBotEngine...")
    bot = PressureBotEngine(data_dir="d:/CricAI/data")
    
    match_id = "1512730" # USA vs Nepal
    query = "What should the USA team avoid to perform better based on their previous and current match?"
    
    print(f"Querying for match {match_id}: '{query}'")
    result = bot.query(match_id, query)
    
    if "error" in result:
        print(f"Error: {result['error']}")
    else:
        print("\n--- Response ---")
        print(result.get("answer"))
        print("\n--- Metadata ---")
        print(f"Match ID: {result.get('match_id')}")
        print(f"Previous Match ID: {result.get('previous_match_id')}")
        print(f"Source: {result.get('source')}")

if __name__ == "__main__":
    test_pressure_bot()
