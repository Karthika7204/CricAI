import pandas as pd

def analyze_player_performance(df, player_name):

    player_data = df[df["striker"] == player_name].copy()

    if player_data.empty:
        return None

    runs = player_data["runs_off_bat"].sum()
    balls = len(player_data)

    strike_rate = (runs / balls) * 100 if balls > 0 else 0

    dot_balls = len(player_data[player_data["runs_off_bat"] == 0])
    dot_ball_pct = (dot_balls / balls) * 100 if balls > 0 else 0

    boundaries = len(player_data[player_data["runs_off_bat"].isin([4,6])])
    boundary_pct = (boundaries / balls) * 100 if balls > 0 else 0

    singles = len(player_data[player_data["runs_off_bat"] == 1])
    singles_pct = (singles / balls) * 100 if balls > 0 else 0

    # ------------------------
    # Phase analysis
    # ------------------------

    player_data["over"] = player_data["ball"].astype(str).str.split(".").str[0].astype(int)

    powerplay = player_data[player_data["over"] <= 6]
    middle = player_data[(player_data["over"] > 6) & (player_data["over"] <= 15)]
    death = player_data[player_data["over"] > 15]

    def phase_strike_rate(data):
        if len(data) == 0:
            return 0
        return (data["runs_off_bat"].sum() / len(data)) * 100

    powerplay_sr = phase_strike_rate(powerplay)
    middle_sr = phase_strike_rate(middle)
    death_sr = phase_strike_rate(death)

    # ------------------------
    # dismissal analysis
    # ------------------------

    dismissals = player_data[player_data["player_dismissed"] == player_name]

    dismissal_types = dismissals["wicket_type"].value_counts().to_dict()

    bowler_dismissals = dismissals["bowler"].value_counts().to_dict()

    # ------------------------
    # scoring pattern
    # ------------------------

    fours = len(player_data[player_data["runs_off_bat"] == 4])
    sixes = len(player_data[player_data["runs_off_bat"] == 6])

    scoring_pattern = {
        "singles": singles,
        "fours": fours,
        "sixes": sixes
    }

    # ------------------------
    # pressure indicator
    # ------------------------

    dot_pressure = dot_ball_pct > 50

    # ------------------------
    # consistency indicator
    # ------------------------

    boundary_dependency = boundary_pct > 25 and singles_pct < 10

    return {

        "runs": runs,
        "balls": balls,

        "strike_rate": strike_rate,
        "dot_ball_pct": dot_ball_pct,
        "boundary_pct": boundary_pct,
        "singles_pct": singles_pct,

        "powerplay_sr": powerplay_sr,
        "middle_sr": middle_sr,
        "death_sr": death_sr,

        "dismissal_types": dismissal_types,
        "bowler_dismissals": bowler_dismissals,

        "scoring_pattern": scoring_pattern,

        "dot_pressure": dot_pressure,
        "boundary_dependency": boundary_dependency
    }