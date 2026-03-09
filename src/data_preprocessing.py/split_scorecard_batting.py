import pandas as pd
import os

# ===== Root Directory =====
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))

# ===== DEFINE FORMAT =====
match_format = "t20"   # change to "odi" / "test"

# Load full batting file
batting_df = pd.read_csv(r"D:\CricAI\data\raw\t20\ICC_Men_s_T20_World_Cup_batting.csv")

match_column = "match_id"

unique_matches = batting_df[match_column].unique()

# ===== OUTPUT FOLDER =====
matches_base_folder = os.path.join(BASE_DIR, "data", "processed", match_format, "matches")

for match_id in unique_matches:
    match_df = batting_df[batting_df[match_column] == match_id]
    
    match_folder = os.path.join(matches_base_folder, str(match_id))
    os.makedirs(match_folder, exist_ok=True)
    
    output_file = os.path.join(match_folder, "batting.csv")
    match_df.to_csv(output_file, index=False)
    
    print(f"Saved Batting → {match_id}")