import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src', 'rag'))

from bundle_matches import bundle_match
from summarizer import generate_summary
from insight_engine import calculate_pre_match_insights

match_id = "1512730"
data_dir = "d:/CricAI/data"

print(f"Bundling match {match_id}...")
bundle_match(match_id, data_dir)

print(f"Generating summary for match {match_id}...")
generate_summary(match_id, data_dir)

print(f"Calculating pre-match insights for match {match_id}...")
calculate_pre_match_insights(match_id, data_dir)

print("Done.")
