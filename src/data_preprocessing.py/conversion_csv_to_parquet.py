import pandas as pd

# Load CSV
df = pd.read_csv(r"D:\CricAI\data\raw\t20\t20_worldcup_2026_match.csv")

# Save as parquet
df.to_parquet(
    r"D:\CricAI\data\processed\t20\match_master.parquet",
    index=False
)

print("Converted successfully ✅")