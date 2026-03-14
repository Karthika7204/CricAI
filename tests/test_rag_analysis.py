import sys
import os
import json

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src', 'rag'))

from engine import QueryEngine

def test_analytical_queries():
    engine = QueryEngine()
    match_id = "1512721" # India vs USA
    
    queries = [
        "What was the match flow?",
        "who won the match",
        "Who is player of the match"
    ]
    
    for query in queries:
        print(f"\nQUERY: {query}")
        result = engine.query(match_id, query)
        print(f"SOURCE: {result.get('source')}")
        print(f"ANSWER:\n{result.get('answer')}")
        print("-" * 50)

if __name__ == "__main__":
    test_analytical_queries()
