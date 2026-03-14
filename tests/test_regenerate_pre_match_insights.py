"""
test_regenerate_pre_match_insights.py
--------------------------------------
Bulk-regenerates pre_match_insights.json for every match folder found under
    data/processed/t20/matches/**/

Run from the repo root:
    python tests/test_regenerate_pre_match_insights.py

What it does:
  1. Discovers all match directories that contain a metadata.pkl file.
  2. Loads the metadata for each match.
  3. Calls PreMatchInsightEngine.generate_insights() to regenerate the JSON.
  4. Reports how many files were updated, how many had non-empty insights,
     and prints a summary table.
"""

import os
import sys
import json
import pickle
import time
import io

# Force UTF-8 output on Windows terminals that default to cp1252
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from pathlib import Path

# ── Allow imports from the src tree ──────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent          # d:/CricAI
sys.path.insert(0, str(ROOT / "src"))

from rag.insight_engine import PreMatchInsightEngine   # noqa: E402

# ── Config ────────────────────────────────────────────────────────────────────
DATA_DIR = ROOT / "data"
MATCHES_DIR = DATA_DIR / "processed" / "t20" / "matches"


def load_metadata(match_folder: Path) -> dict:
    """Load metadata.pkl; fall back to an empty dict if not found."""
    meta_path = match_folder / "metadata.pkl"
    if meta_path.exists():
        with open(meta_path, "rb") as f:
            return pickle.load(f)
    return {}


def run():
    engine = PreMatchInsightEngine(data_dir=str(DATA_DIR))

    match_dirs = sorted(
        [d for d in MATCHES_DIR.iterdir() if d.is_dir()]
    )

    if not match_dirs:
        print("❌  No match folders found under:", MATCHES_DIR)
        sys.exit(1)

    print(f"\n{'='*60}")
    print(f"  Regenerating pre_match_insights.json for {len(match_dirs)} matches")
    print(f"{'='*60}\n")

    results = []
    total_start = time.time()

    for match_dir in match_dirs:
        match_id = match_dir.name
        metadata = load_metadata(match_dir)

        try:
            start = time.time()
            insights = engine.generate_insights(match_id, metadata)
            elapsed = time.time() - start

            has_ranking_races   = len(insights.get("ranking_races", [])) > 0
            has_milestone_watch = len(insights.get("milestone_watch", [])) > 0
            has_pb_watch        = len(insights.get("personal_best_watch", [])) > 0
            is_empty            = not (has_ranking_races or has_milestone_watch or has_pb_watch)

            status = "[OK]   " if not is_empty else "[EMPTY]"
            print(
                f"  [{match_id}]  {status}  |  "
                f"ranking_races={len(insights.get('ranking_races', []))}  "
                f"milestones={len(insights.get('milestone_watch', []))}  "
                f"({elapsed:.2f}s)"
            )
            sys.stdout.flush()

            results.append({
                "match_id": match_id,
                "ok": True,
                "empty": is_empty,
                "ranking_races": len(insights.get("ranking_races", [])),
                "milestones": len(insights.get("milestone_watch", [])),
                "elapsed": round(elapsed, 2),
            })

        except Exception as exc:
            print(f"  [{match_id}]  [ERROR] {exc}")
            results.append({"match_id": match_id, "ok": False, "error": str(exc)})

    total_elapsed = time.time() - total_start

    # ── Summary ───────────────────────────────────────────────────────────────
    succeeded = [r for r in results if r.get("ok")]
    failed    = [r for r in results if not r.get("ok")]
    non_empty = [r for r in succeeded if not r.get("empty", True)]

    print(f"\n{'='*60}")
    print(f"  SUMMARY")
    print(f"{'='*60}")
    print(f"  Total matches processed : {len(results)}")
    print(f"  [PASS]  Succeeded       : {len(succeeded)}")
    print(f"  [DATA]  Non-empty data  : {len(non_empty)}")
    print(f"  [WARN]  Still empty     : {len(succeeded) - len(non_empty)}")
    print(f"  [FAIL]  Errors          : {len(failed)}")
    print(f"  [TIME]  Total time      : {total_elapsed:.1f}s")

    if failed:
        print("\n  Failed match IDs:")
        for r in failed:
            print(f"    • {r['match_id']}  →  {r.get('error', 'unknown')}")

    if succeeded and len(non_empty) == 0:
        print("\n  [WARN] ALL files regenerated but insights are empty.")
        print("         Check that ICC ranking CSVs and career CSVs are present in data/raw/")

    print(f"\n{'='*60}\n")

    # Return a non-zero exit code if any match failed
    sys.exit(len(failed))


if __name__ == "__main__":
    run()
