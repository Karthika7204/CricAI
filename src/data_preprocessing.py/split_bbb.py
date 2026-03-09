import pandas as pd
import os

# ===== DEFINE FORMAT =====
match_format = "t20"   # change to "odi" / "test"

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))

# ===== INPUT FILE =====
bbb_file = os.path.join(BASE_DIR, "data", "raw", match_format, f"{match_format}_worldcup_2026_bbb.csv")

# ===== OUTPUT FOLDER =====
matches_base_folder = os.path.join(BASE_DIR, "data", "processed", match_format, "matches")

df = pd.read_csv(bbb_file)

match_column = "match_id"

unique_matches = df[match_column].unique()


for match_id in unique_matches:
    match_df = df[df[match_column] == match_id]

    match_folder = os.path.join(matches_base_folder, str(match_id))
    os.makedirs(match_folder, exist_ok=True)

    output_file = os.path.join(match_folder, "bbb.csv")
    match_df.to_csv(output_file, index=False)

print("Done ✅")