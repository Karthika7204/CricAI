import pandas as pd
import os
from glob import glob

# Base folder
base_path = r"D:\CricAI\data\raw\career\t20\batting"

# Get all country files
all_files = glob(os.path.join(base_path, "*_all_players_career.csv"))

print("Files Found:", len(all_files))

df_list = []

for file in all_files:
    temp_df = pd.read_csv(file)
    
    # Ensure country column exists
    if "country" not in temp_df.columns:
        # Extract country from filename
        country = os.path.basename(file).split("_")[0]
        temp_df["country"] = country
    
    df_list.append(temp_df)

# Merge everything
master_df = pd.concat(df_list, ignore_index=True)

print("Total Rows:", len(master_df))

# Save consolidated file
output_path = r"D:\CricAI\data\processed\career\t20_batting_master.parquet"
master_df.to_parquet(output_path, index=False)

print("Master file created ✅")