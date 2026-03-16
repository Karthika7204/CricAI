import os
from pathlib import Path
import pandas as pd

def load_datasets():
    # Base directory for the project
    base_dir = Path(__file__).resolve().parent.parent.parent
    data_dir = base_dir / "data" / "raw" / "training_assitent"

    deliveries1 = pd.read_csv(data_dir / "deliveries_updated_ipl_upto_2025.csv")
    deliveries2 = pd.read_csv(data_dir / "deliveries_updated_mens_ipl.csv")
    deliveries3 = pd.read_csv(data_dir / "IPL_ball_by_ball_updated.csv")

    matches = pd.read_csv(data_dir / "matches_updated_ipl_upto_2025.csv")

    players = pd.read_csv(data_dir / "all_players-data-updated.csv")

    # combine all ball-by-ball datasets
    ball_by_ball = pd.concat([deliveries1, deliveries2, deliveries3], ignore_index=True)

    # clean column names
    ball_by_ball.columns = ball_by_ball.columns.str.strip()
    matches.columns = matches.columns.str.strip()
    players.columns = players.columns.str.strip()

    return {
        "ball_by_ball": ball_by_ball,
        "matches": matches,
        "players": players
    }