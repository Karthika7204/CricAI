import pandas as pd
import os
from glob import glob

# Base folder for bowling career CSVs
base_path = r"D:\CricAI\data\raw\career\t20\bowling"

# Get all country bowling career files
all_files = glob(os.path.join(base_path, "*_all_players_career_bowling.csv"))

print("Files Found:", len(all_files))
for f in all_files:
    print(" ", os.path.basename(f))

df_list = []

for file in all_files:
    temp_df = pd.read_csv(file)
    
    # Ensure country column exists
    if "country" not in temp_df.columns:
        # Extract country from filename (e.g., India_all_players_career_bowling.csv -> India)
        country = os.path.basename(file).split("_all_players")[0].replace("_", " ")
        temp_df["country"] = country
    
    df_list.append(temp_df)

if not df_list:
    print("No bowling career files found. Exiting.")
    exit(1)

# Merge all country files
master_df = pd.concat(df_list, ignore_index=True)

print("Total Rows:", len(master_df))
print("Columns:", master_df.columns.tolist())

# Save consolidated bowling career master
output_path = r"D:\CricAI\data\processed\career\t20_bowling_master.parquet"
master_df.to_parquet(output_path, index=False)

print(f"Bowling career master saved to: {output_path} [OK]")
