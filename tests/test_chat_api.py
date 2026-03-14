import requests
import json
import sys

def test_chat_post():
    url = "http://localhost:8000/api/chat"
    payload = {
        "match_id": "1512768",
        "query": "what is the turning point of this match"
    }
    headers = {
        "Content-Type": "application/json"
    }

    print(f"Testing POST {url} with match_id: {payload['match_id']}")
    try:
        response = requests.post(url, data=json.dumps(payload), headers=headers, timeout=30)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("Response:")
            print(json.dumps(response.json(), indent=2))
        else:
            print("Error Response:")
            print(response.text)
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the backend. Is app.py running?")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    test_chat_post()
