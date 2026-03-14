"""
test_bulk_process_new_matches.py
---------------------------------
Runs the full CricAI bot pipeline for a specific range of match IDs.
Skips matches whose directories don't exist yet.

Pipeline per match (6 steps):
  1. bundle_match          -> batting.csv / bowling.csv / bbb.csv / context.json
  2. generate_summary      -> structured_summary.json          (LLM)
  3. calculate_pre_match_insights -> pre_match_insights.json   (stats)
  4. run_preprocessing     -> index.faiss / chunks.pkl / metadata.pkl
  5. get_pvp_comparison    -> pvp_comparison.json              (engine)
  6. calculate_awards      -> awards.json                      (engine)

Configure the range below, then run from the repo root:
    python tests/test_bulk_process_new_matches.py

Optional flags (set as constants below):
  SKIP_IF_EXISTS  - skip an individual step if its output file already exists
  DELAY_SECONDS   - pause between matches (kind to LLM rate limits)
"""

import sys
import os
import time
from pathlib import Path

# ── Force UTF-8 on Windows PowerShell terminals ───────────────────────────────
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# ── Repo root + src on path ───────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent      # d:/CricAI
SRC  = ROOT / "src"
sys.path.insert(0, str(SRC))
sys.path.insert(0, str(SRC / "rag"))

# ── Import pipeline modules ────────────────────────────────────────────────────
from rag.bundle_matches        import bundle_match
from rag.summarizer            import generate_summary
from rag.insight_engine        import calculate_pre_match_insights
from rag.preprocess            import run_preprocessing
from rag.pvp_analysis          import get_pvp_comparison
from rag.award_engine          import calculate_awards
from flow.match_flow_engine    import MatchFlowEngine

# ── Configuration ─────────────────────────────────────────────────────────────
DATA_DIR      = str(ROOT / "data")
MATCHES_ROOT  = ROOT / "data" / "processed" / "t20" / "matches"

MATCH_ID_START  = 1512768       # <-- first match to process
MATCH_ID_END    = 1512768       # <-- last  match to process (inclusive)

SKIP_IF_EXISTS  = False         # True = skip a step if its output already exists
DELAY_SECONDS   = 2            # seconds to wait between matches (set 0 for no delay)

# ── Step output files (used when SKIP_IF_EXISTS=True) ─────────────────────────
STEP_OUTPUTS = {
    "bundle":    ["batting.csv", "bowling.csv", "bbb.csv"],
    "summary":   ["structured_summary.json"],
    "insights":  ["pre_match_insights.json"],
    "faiss":     ["index.faiss", "chunks.pkl", "metadata.pkl"],
    "pvp":       ["pvp_comparison.json"],
    "awards":    ["awards.json"],
}


def _all_exist(match_folder: Path, keys: list[str]) -> bool:
    return all((match_folder / k).exists() for k in keys)


def process_single_match(match_id: str, flow_engine: MatchFlowEngine) -> dict:
    """
    Run all 6 pipeline steps for one match.
    Returns a result dict with per-step status.
    """
    match_folder = MATCHES_ROOT / match_id
    results = {}

    print(f"\n{'='*55}")
    print(f"  PIPELINE  |  match {match_id}")
    print(f"{'='*55}")








    # ── Step 1: Bundle ────────────────────────────────────────────────────────
    step = "bundle"
    if SKIP_IF_EXISTS and _all_exist(match_folder, STEP_OUTPUTS[step]):
        print(f"  [1/6] bundle_match       ... SKIP (exists)")
        results[step] = "skipped"
    else:
        try:
            print(f"  [1/6] bundle_match       ...", end=" ", flush=True)
            bundle_match(match_id, DATA_DIR)
            print("OK")
            results[step] = "ok"
        except Exception as e:
            print(f"ERROR: {e}")
            results[step] = f"error: {e}"
            print(f"  [!] bundle failed - aborting match {match_id}")
            return results   # Can't continue without raw CSVs

    # ── Step 2: AI Summary ────────────────────────────────────────────────────
    step = "summary"
    if SKIP_IF_EXISTS and _all_exist(match_folder, STEP_OUTPUTS[step]):
        print(f"  [2/6] generate_summary   ... SKIP (exists)")
        results[step] = "skipped"
    else:
        try:
            print(f"  [2/6] generate_summary   ...", end=" ", flush=True)
            generate_summary(match_id, DATA_DIR)
            print("OK")
            results[step] = "ok"
        except Exception as e:
            print(f"ERROR: {e}")
            results[step] = f"error: {e}"
            # Non-fatal: other steps can still run

    # ── Step 3: Pre-Match Insights ────────────────────────────────────────────
    step = "insights"
    if SKIP_IF_EXISTS and _all_exist(match_folder, STEP_OUTPUTS[step]):
        print(f"  [3/6] pre_match_insights ... SKIP (exists)")
        results[step] = "skipped"
    else:
        try:
            print(f"  [3/6] pre_match_insights ...", end=" ", flush=True)
            calculate_pre_match_insights(match_id, DATA_DIR)
            print("OK")
            results[step] = "ok"
        except Exception as e:
            print(f"ERROR: {e}")
            results[step] = f"error: {e}"

    # ── Step 4: FAISS Preprocessing ───────────────────────────────────────────
    step = "faiss"
    if SKIP_IF_EXISTS and _all_exist(match_folder, STEP_OUTPUTS[step]):
        print(f"  [4/6] run_preprocessing  ... SKIP (exists)")
        results[step] = "skipped"
    else:
        try:
            print(f"  [4/6] run_preprocessing  ...", end=" ", flush=True)
            run_preprocessing(match_id, DATA_DIR)
            print("OK")
            results[step] = "ok"
        except Exception as e:
            print(f"ERROR: {e}")
            results[step] = f"error: {e}"

    # ── Step 5: PvP Comparison ────────────────────────────────────────────────
    step = "pvp"
    if SKIP_IF_EXISTS and _all_exist(match_folder, STEP_OUTPUTS[step]):
        print(f"  [5/6] pvp_comparison     ... SKIP (exists)")
        results[step] = "skipped"
    else:
        try:
            print(f"  [5/6] pvp_comparison     ...", end=" ", flush=True)
            get_pvp_comparison(match_id, DATA_DIR, force_refresh=True)
            print("OK")
            results[step] = "ok"
        except Exception as e:
            print(f"ERROR: {e}")
            results[step] = f"error: {e}"

    # ── Step 6: Awards ────────────────────────────────────────────────────────
    step = "awards"
    if SKIP_IF_EXISTS and _all_exist(match_folder, STEP_OUTPUTS[step]):
        print(f"  [6/6] calculate_awards   ... SKIP (exists)")
        results[step] = "skipped"
    else:
        try:
            print(f"  [6/6] calculate_awards   ...", end=" ", flush=True)
            calculate_awards(match_id, DATA_DIR)
            print("OK")
            results[step] = "ok"
        except Exception as e:
            print(f"ERROR: {e}")
            results[step] = f"error: {e}"

    return results


def main():
    match_ids = [
        str(mid)
        for mid in range(MATCH_ID_START, MATCH_ID_END + 1)
        if (MATCHES_ROOT / str(mid)).is_dir()
    ]

    skipped_ids = [
        str(mid)
        for mid in range(MATCH_ID_START, MATCH_ID_END + 1)
        if not (MATCHES_ROOT / str(mid)).is_dir()
    ]

    total_range = MATCH_ID_END - MATCH_ID_START + 1
    print(f"\n{'#'*55}")
    print(f"  CricAI Bulk Pipeline  |  {MATCH_ID_START} -> {MATCH_ID_END}")
    print(f"  Range size : {total_range}")
    print(f"  Found      : {len(match_ids)} match folders")
    print(f"  Missing    : {len(skipped_ids)} (will skip)")
    print(f"{'#'*55}")

    if skipped_ids:
        print(f"\n  [INFO] No folder for: {', '.join(skipped_ids)}")

    if not match_ids:
        print("\n  Nothing to process. Exiting.")
        sys.exit(0)

    flow_engine  = MatchFlowEngine(data_root=str(MATCHES_ROOT))
    all_results  = {}
    total_start  = time.time()

    for idx, match_id in enumerate(match_ids, 1):
        print(f"\n  Processing {idx}/{len(match_ids)}  (match {match_id})")
        all_results[match_id] = process_single_match(match_id, flow_engine)

        if DELAY_SECONDS > 0 and idx < len(match_ids):
            print(f"  [pause {DELAY_SECONDS}s ...]")
            time.sleep(DELAY_SECONDS)

    # ── Final Summary Table ───────────────────────────────────────────────────
    steps = ["bundle", "summary", "insights", "faiss", "pvp", "awards"]
    total_elapsed = time.time() - total_start

    print(f"\n{'#'*55}")
    print(f"  SUMMARY")
    print(f"{'#'*55}")
    header = f"  {'Match':<12}" + "".join(f"{s:<10}" for s in steps)
    print(header)
    print(f"  {'-'*52}")

    errors_found = False
    for mid, res in all_results.items():
        row_parts = []
        for s in steps:
            val = res.get(s, "n/a")
            if val == "ok":
                cell = "[OK]    "
            elif val == "skipped":
                cell = "[SKIP]  "
            elif val.startswith("error"):
                cell = "[ERR]   "
                errors_found = True
            else:
                cell = f"{val[:8]:<8}"
            row_parts.append(cell)
        print(f"  {mid:<12}" + "  ".join(row_parts))

    print(f"\n  Total time : {total_elapsed:.1f}s")
    if errors_found:
        print("  [WARN] Some steps had errors - review output above.")
    else:
        print("  [PASS] All steps completed successfully.")
    print(f"{'#'*55}\n")

    sys.exit(1 if errors_found else 0)


if __name__ == "__main__":
    main()
