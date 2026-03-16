import pandas as pd


def analyze_player_matchups(df, player_name):

    player_data = df[df["striker"] == player_name]

    if player_data.empty:
        return None

    # Find dismissals
    dismissals = player_data[player_data["player_dismissed"] == player_name]

    bowler_dismissals = dismissals["bowler"].value_counts()

    if bowler_dismissals.empty:
        return {
            "danger_bowler": "None",
            "dismissals": 0,
            "strike_rate": "N/A"
        }

    danger_bowler = bowler_dismissals.idxmax()
    dismissals_count = bowler_dismissals.max()

    # Calculate strike rate vs that bowler
    matchup_data = player_data[player_data["bowler"] == danger_bowler]

    runs = matchup_data["runs_off_bat"].sum()
    balls = len(matchup_data)

    strike_rate = (runs / balls) * 100 if balls > 0 else 0

    return {
        "danger_bowler": danger_bowler,
        "dismissals": dismissals_count,
        "strike_rate": round(strike_rate, 2)
    }