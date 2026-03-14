"""
bulk_process_matches.py
=======================
Script to iteratively run the entire CricAI generation pipeline for all matches 
found in the data directory. It safely handles errors per-match to ensure the 
pipeline continues processing even if one match faces issues (like missing data 
or rate limits).

Usage:
    python bulk_process_matches.py
"""

import sys
import os
import time
from pathlib import Path

# Add src to path to import local modules correctly
sys.path.append(os.path.join(os.path.dirname(__file__), 'rag'))
sys.path.append(os.path.dirname(__file__))

# Import the engine functions
from rag.bundle_matches import bundle_match
from rag.summarizer import generate_summary
from rag.insight_engine import calculate_pre_match_insights
from rag.preprocess import run_preprocessing
from rag.pvp_analysis import get_pvp_comparison
from rag.award_engine import calculate_awards
from flow.match_flow_engine import MatchFlowEngine

DATA_DIR = "d:/CricAI/data"
MATCHES_ROOT = os.path.join(DATA_DIR, "processed", "t20", "matches")

def process_single_match(match_id: str, flow_engine: MatchFlowEngine):
    """Run all CricAI pipeline steps for a single match."""
    print(f"\n" + "="*50)
    print(f"🚀 STARTING PIPELINE FOR MATCH: {match_id}")
    print("="*50)
    
    # 1. Bundle Matches
    try:
        print(f"[{match_id}] 1/7 Bundling Match...")
        bundle_match(match_id, DATA_DIR)
    except Exception as e:
        print(f"❌ Error bundling {match_id}: {e}")
        return False

    # 2. Generate Summary (LLM)
    try:
        print(f"[{match_id}] 2/7 Generating AI Summary...")
        generate_summary(match_id, DATA_DIR)
    except Exception as e:
        print(f"❌ Error in summarizer for {match_id}: {e}")
        # Note: We do not return False here. We want to allow independent
        # engines like pre-match insights, pvp, and awards to run even 
        # if the LLM summarizer fails (e.g. due to rate limits).

    # 3. Pre-Match Insights (LLM)
    try:
        print(f"[{match_id}] 3/7 Calculating Pre-Match Insights...")
        calculate_pre_match_insights(match_id, DATA_DIR)
    except Exception as e:
        print(f"❌ Error in insights for {match_id}: {e}")

    # 4. RAG Preprocessing (FAISS Indexing + Chunking)
    try:
        print(f"[{match_id}] 4/7 Running FAISS Preprocessing...")
        run_preprocessing(match_id, DATA_DIR)
    except Exception as e:
        print(f"❌ Error in FAISS preprocessing for {match_id}: {e}")

    # 5. PvP Comparison (Engine + Cache)
    try:
        print(f"[{match_id}] 5/7 Generating PvP Comparison...")
        get_pvp_comparison(match_id, DATA_DIR, force_refresh=True)
    except Exception as e:
        print(f"❌ Error in PvP comparison for {match_id}: {e}")

    # 6. Awards Engine (Deterministic)
    try:
        print(f"[{match_id}] 6/7 Calculating Post-Match Awards...")
        calculate_awards(match_id, DATA_DIR)
    except Exception as e:
        print(f"❌ Error generating awards for {match_id}: {e}")

   

def main():
    if not os.path.exists(MATCHES_ROOT):
        print(f"Error: matches root {MATCHES_ROOT} does not exist.")
        sys.exit(1)

    # Initialize reusable engines
    flow_engine = MatchFlowEngine(data_root=MATCHES_ROOT)

    # Gather all match IDs
    match_ids = [
        d for d in os.listdir(MATCHES_ROOT) 
        if os.path.isdir(os.path.join(MATCHES_ROOT, d))
    ]
    
    print(f"Found {len(match_ids)} matches to process.")
    
    success_count = 0
    failure_count = 0

    for idx, match_id in enumerate(match_ids, 1):
        print(f"\nProcessing {idx}/{len(match_ids)}...")
        success = process_single_match(match_id, flow_engine)
        
        if success:
            success_count += 1
        else:
            failure_count += 1
            
        # Optional: Sleep slightly to be polite to LLM limits if processing in massive bulk
        time.sleep(2)

    print("\n" + "#"*50)
    print("🎯 BULK PROCESSING COMPLETE")
    print(f"Successfully processed: {success_count}/{len(match_ids)}")
    print(f"Failures (Check logs): {failure_count}")
    print("#"*50 + "\n")

if __name__ == "__main__":
    main()
