import re
from router import Router

metadata = {
    "all_players": ["Suryakumar Yadav", "SA Yadav", "Arshdeep Singh"],
    "winner": "India",
    "score": "119",
    "margin": "6 runs",
    "margin_type": "runs",
    "venue": "New York",
    "date": "June 9, 2024",
    "toss_winner": "Pakistan"
}

router = Router(metadata)
queries = [
    "What are the key matchups for Suryakumar Yadav?",
    "What should the bowling rotation be for India?",
    "What should the USA team avoid to perform better?"
]

print("Routing results:")
for q in queries:
    res = router.route(q)
    print(f"Query: {q} -> Route: {res}")
