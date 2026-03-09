import pandas as pd


career_df = pd.read_parquet(r"D:\CricAI\data\processed\career_master_t20.parquet")

career_df[career_df["country"] == "India"]

print(career_df)