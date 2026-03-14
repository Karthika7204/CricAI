"""
test_router_pressure.py — Test routing of pressure queries
"""
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src', 'rag'))

from engine import QueryEngine

def test_routing():
    print("Initializing QueryEngine...")
    engine = QueryEngine(data_dir="d:/CricAI/data")
    
    match_id = "1512721"
    tests = [
        "What should the USA team avoid to perform better?",
        "Give me some pressure insights for this match",
        "How can India improve their performance?"
    ]
    
    print(f"--- Testing Routing for Match {match_id} ---")
    for q in tests:
        print(f"\nQuery: {q}")
        result = engine.query(match_id, q)
        source = result.get("source")
        print(f"Routed to: {source}")
        if source == "pressure_recommendation_bot":
            print("SUCCESS: Correctly routed to Pressure Bot.")
        else:
            print(f"FAILURE: Routed to {source} instead of pressure_recommendation_bot.")

if __name__ == "__main__":
    test_routing()
