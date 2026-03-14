import requests
import json

url = "http://localhost:8000/api/chat"
queries = [
    "What are the key matchups for Suryakumar Yadav?",
    "What should the bowling rotation be for India?",
    "What should the USA team avoid to perform better?"
]

for q in queries:
    print(f"\nQuery: {q}")
    payload = {"match_id": "1512730", "query": q}
    try:
        response = requests.post(url, json=payload)
        print(f"Source: {response.json().get('source')}")
        print(f"Answer: {response.json().get('answer')}")
    except Exception as e:
        print(f"Error: {e}")
