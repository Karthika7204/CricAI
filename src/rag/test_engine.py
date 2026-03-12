from engine import QueryEngine
import json

def test_engine():
    engine = QueryEngine()
    match_id = "1512721"
    
    test_queries = [
        "Who is good and bad against Surya Kumar Yadav in this match?"
    ]
    
    print(f"--- Testing V5 Query Engine for Match {match_id} ---")
    for q in test_queries:
        print(f"\nUser: {q}")
        result = engine.query(match_id, q)
        
        if "answer" in result:
            print(f"Answer ({result['source']}): {result['answer']}")
        elif "prompt" in result:
            print(f"RAG Prompt generated (Grounding chunks: {len(result['retrieved_chunks'])})")
            if "error" in result:
                print(f"Note: {result['error']}")
        else:
            print(f"Error: {result.get('error')}")

if __name__ == "__main__":
    test_engine()
