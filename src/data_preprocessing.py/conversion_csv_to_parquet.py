import pandas as pd

# Load CSV
df = pd.read_csv(r"D:\CricAI\data\raw\t20\t20_worldcup_2026_bbb.csv")

# Save as parquet
df.to_parquet(
    r"D:\CricAI\data\processed\t20\bbb_match_data.parquet",
    index=False
)

print("Converted successfully ✅")