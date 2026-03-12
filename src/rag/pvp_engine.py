"""
pvp_engine.py — Player vs Player Comparison Engine
====================================================
Standalone engine that generates per-match head-to-head comparison reports.

DATA SOURCES (primary → secondary):
  1. t20s_player_vs_bowler.csv   — direct H2H: batter vs bowler
  2. t20s_player_vs_team.csv     — batter performance vs opponent team
  3. t20_master.parquet          — batting career stats
  4. t20_bowling_master.parquet  — bowling career stats
  5. batting_scorecard.parquet   — recent form (batting)
  6. bowling_scorecard.parquet   — recent form (bowling)

Output JSON: data/processed/t20/matches/<match_id>/pvp_comparison.json
"""

import pandas as pd
import json
import pickle
import os
from pathlib import Path


# ─────────────────────────────────────────────
# VERDICT THRESHOLDS
# ─────────────────────────────────────────────
MIN_BALLS_FOR_H2H   = 6     # minimum balls faced to consider H2H reliable
BOWLER_EDGE_DIMISS  = 2     # dismissals >= this → bowler edge
BATTER_EDGE_SR      = 130.0 # strike rate >= this in H2H → batter edge
BATTER_EDGE_AVG     = 35.0  # career batting average for a "strong" batter


class PvPComparisonEngine:
    """
    Generates Player vs Player comparison data for a specific match.
    Reads all data sources once at init; is fully standalone (no chatbot).
    """

    def __init__(self, data_dir: str = "d:/CricAI/data"):
        self.data_dir = Path(data_dir)

        # ── Primary H2H tables ──
        pvp_dir = self.data_dir / "raw" / "tournament" / "Player matching t20 data"
        self.df_h2h  = pd.read_csv(pvp_dir / "t20s_player_vs_bowler.csv")
        self.df_team = pd.read_csv(pvp_dir / "t20s_player_vs_team.csv")

        # ── Career tables ──
        career_dir = self.data_dir / "processed" / "career"
        self.df_bat_career  = pd.read_parquet(career_dir / "t20_master.parquet")
        self.df_bowl_career = pd.read_parquet(career_dir / "t20_bowling_master.parquet")

        # ── Scorecard tables ──
        t20_dir = self.data_dir / "processed" / "t20"
        self.df_bat_sc  = pd.read_parquet(t20_dir / "batting_scorecard.parquet")
        self.df_bowl_sc = pd.read_parquet(t20_dir / "bowling_scorecard.parquet")

        # Normalise name columns for matching
        self.df_h2h["batter"]  = self.df_h2h["batter"].str.strip()
        self.df_h2h["bowler"]  = self.df_h2h["bowler"].str.strip()
        self.df_team["player"] = self.df_team["player"].str.strip()
        self.df_team["opponent_team"] = self.df_team["opponent_team"].str.strip()
        self.df_bat_career["player_name"]  = self.df_bat_career["player_name"].str.strip()
        self.df_bowl_career["player_name"] = self.df_bowl_career["player_name"].str.strip()
        self.df_bat_sc["player"]  = self.df_bat_sc["player"].str.strip()
        self.df_bowl_sc["player"] = self.df_bowl_sc["player"].str.strip()

    # ──────────────────────────────────────────
    # Internal: load teams from match metadata
    # ──────────────────────────────────────────
    def _get_match_players(self, match_id: str) -> dict:
        """
        Returns {'team_a': name, 'team_b': name,
                 'players_a': [...], 'players_b': [...]}

        Strategy:
        1. Reads teams from metadata.pkl `captains` dict (team names are keys)
        2. Reads players per team from batting + bowling scorecards filtered by match_id
        """
        meta_path = (
            self.data_dir / "processed" / "t20" / "matches"
            / match_id / "metadata.pkl"
        )
        if not meta_path.exists():
            raise FileNotFoundError(f"metadata.pkl not found for match {match_id}")

        with open(meta_path, "rb") as f:
            meta = pickle.load(f)

        # ── Get team names from captains dict (or legacy keys) ──
        captains = meta.get("captains", {})
        team_names = list(captains.keys())

        if len(team_names) >= 2:
            team_a, team_b = team_names[0], team_names[1]
        else:
            team_a = meta.get("team1", "")
            team_b = meta.get("team2", "")

        # ── Get players from batting scorecard for this match ──
        mid_int = int(match_id)
        match_bat = self.df_bat_sc[self.df_bat_sc["match_id"] == mid_int]
        match_bowl = self.df_bowl_sc[self.df_bowl_sc["match_id"] == mid_int]

        def _get_players_for_team(team_name):
            bat  = set(match_bat[match_bat["team"] == team_name]["player"].tolist())
            bowl = set(match_bowl[match_bowl["team"] == team_name]["player"].tolist())
            return list(bat | bowl)

        players_a = _get_players_for_team(team_a)
        players_b = _get_players_for_team(team_b)

        return {
            "team_a": team_a,
            "team_b": team_b,
            "players_a": players_a,
            "players_b": players_b,
        }

    # ──────────────────────────────────────────
    # Head-to-Head: batsman vs bowler
    # ──────────────────────────────────────────
    def _get_h2h(self, batsman: str, bowler: str) -> dict:
        row = self.df_h2h[
            (self.df_h2h["batter"] == batsman) &
            (self.df_h2h["bowler"] == bowler)
        ]
        if row.empty:
            return {"found": False, "balls": 0, "runs": 0, "dismissals": 0, "strike_rate": None}
        r = row.iloc[0]
        return {
            "found": True,
            "balls": int(r["balls"]),
            "runs":  int(r["runs"]),
            "dismissals": int(r["dismissals"]),
            "strike_rate": round(float(r["strike_rate"]), 2),
        }

    # ──────────────────────────────────────────
    # Batsman vs opponent TEAM
    # ──────────────────────────────────────────
    def _get_vs_team(self, batsman: str, opponent_team: str) -> dict:
        row = self.df_team[
            (self.df_team["player"] == batsman) &
            (self.df_team["opponent_team"] == opponent_team)
        ]
        if row.empty:
            return {"found": False}
        r = row.iloc[0]
        return {
            "found": True,
            "runs": int(r["runs"]),
            "balls": int(r["balls"]),
            "dismissals": int(r["dismissals"]),
            "average": round(float(r["average"]), 2),
            "strike_rate": round(float(r["strike_rate"]), 2),
        }

    # ──────────────────────────────────────────
    # Career stats
    # ──────────────────────────────────────────
    def _get_career_batting(self, player: str) -> dict:
        row = self.df_bat_career[self.df_bat_career["player_name"] == player]
        if row.empty:
            return {"found": False}
        r = row.iloc[0]
        return {
            "found": True,
            "matches": int(r["matches"]),
            "runs":    int(r["total_runs"]),
            "average": round(float(r["average"]), 2) if pd.notna(r["average"]) else None,
            "strike_rate": round(float(r["strike_rate"]), 2) if pd.notna(r["strike_rate"]) else None,
            "fifties":  int(r["fifties"]),
            "hundreds": int(r["hundreds"]),
        }

    def _get_career_bowling(self, player: str) -> dict:
        row = self.df_bowl_career[self.df_bowl_career["player_name"] == player]
        if row.empty:
            return {"found": False}
        r = row.iloc[0]
        return {
            "found": True,
            "matches": int(r["matches"]),
            "wickets": int(r["wickets"]),
            "average": round(float(r["average"]), 2) if pd.notna(r["average"]) else None,
            "economy": round(float(r["economy"]), 2) if pd.notna(r["economy"]) else None,
            "best_bowling": str(r["best_bowling"]),
        }

    # ──────────────────────────────────────────
    # Recent form (last N scorecard entries)
    # ──────────────────────────────────────────
    def _get_recent_form_batting(self, player: str, n: int = 3) -> list:
        rows = (
            self.df_bat_sc[self.df_bat_sc["player"] == player]
            .sort_values("date", ascending=False)
            .head(n)
        )
        result = []
        for _, r in rows.iterrows():
            result.append({
                "match_id": str(r["match_id"]),
                "date": str(r["date"]),
                "runs": int(r["runs"]),
                "balls_faced": int(r["balls_faced"]),
                "strike_rate": round(float(r["strike_rate"]), 2) if pd.notna(r["strike_rate"]) else None,
            })
        return result

    def _get_recent_form_bowling(self, player: str, n: int = 3) -> list:
        rows = (
            self.df_bowl_sc[self.df_bowl_sc["player"] == player]
            .sort_values("date", ascending=False)
            .head(n)
        )
        result = []
        for _, r in rows.iterrows():
            result.append({
                "match_id": str(r["match_id"]),
                "date": str(r["date"]),
                "wickets": int(r["wickets"]),
                "runs_conceded": int(r["runs_conceded"]),
                "overs": float(r["overs"]),
                "economy": round(float(r["economy"]), 2) if pd.notna(r["economy"]) else None,
            })
        return result

    # ──────────────────────────────────────────
    # Verdict generator (rule-based, deterministic)
    # ──────────────────────────────────────────
    def _generate_verdict(
        self,
        h2h: dict,
        vs_team: dict,
        bat_career: dict,
        bowl_career: dict,
    ) -> dict:
        """
        Determines who has the edge in a matchup.
        Returns: { "winner": "batsman"|"bowler"|"neutral", "reason": str }
        """
        reasons = []
        bat_score  = 0
        bowl_score = 0

        # ── Layer 1: Direct H2H ──
        if h2h["found"] and h2h["balls"] >= MIN_BALLS_FOR_H2H:
            if h2h["dismissals"] >= BOWLER_EDGE_DIMISS:
                bowl_score += 3
                reasons.append(
                    f"Bowler has dismissed {h2h['batsman_name'] if 'batsman_name' in h2h else 'the batsman'} "
                    f"{h2h['dismissals']}x in {h2h['balls']} balls (H2H)"
                )
            elif h2h["strike_rate"] is not None and h2h["strike_rate"] >= BATTER_EDGE_SR and h2h["dismissals"] <= 1:
                bat_score += 3
                reasons.append(
                    f"Batsman has SR {h2h['strike_rate']} in H2H with only "
                    f"{h2h['dismissals']} dismissal(s) in {h2h['balls']} balls"
                )
            else:
                reasons.append(
                    f"H2H: {h2h['runs']} runs off {h2h['balls']} balls "
                    f"({h2h['dismissals']} dismissals, SR {h2h['strike_rate']})"
                )
        else:
            reasons.append("No reliable head-to-head data — verdict based on career & team record")

        # ── Layer 2: Batsman vs Opponent Team ──
        if vs_team["found"]:
            team_avg = vs_team.get("average", 0) or 0
            team_sr  = vs_team.get("strike_rate", 0) or 0
            if team_avg >= BATTER_EDGE_AVG and team_sr >= BATTER_EDGE_SR:
                bat_score += 2
                reasons.append(
                    f"Batsman averages {team_avg} @ SR {team_sr} vs this team "
                    f"({vs_team['runs']} runs in {vs_team['balls']} balls)"
                )
            elif vs_team["dismissals"] >= BOWLER_EDGE_DIMISS and vs_team["balls"] >= 12:
                bowl_score += 2
                reasons.append(
                    f"Batsman has struggled vs this team: {vs_team['dismissals']} dismissals "
                    f"in {vs_team['balls']} balls (avg {team_avg})"
                )

        # ── Layer 3: Career Form Tiebreak ──
        if bat_score == bowl_score:
            bat_avg  = (bat_career.get("average") or 0)
            bat_sr   = (bat_career.get("strike_rate") or 0)
            bowl_avg = (bowl_career.get("average") or 99)
            bowl_econ= (bowl_career.get("economy") or 10)
            if bat_avg >= 30 and bat_sr >= 130:
                bat_score += 1
                reasons.append(f"Strong batter by career: avg {bat_avg}, SR {bat_sr}")
            if bowl_avg <= 25 and bowl_econ <= 8.0:
                bowl_score += 1
                reasons.append(f"Dangerous bowler by career: avg {bowl_avg}, econ {bowl_econ}")

        # ── Final Verdict ──
        if bowl_score > bat_score:
            winner = "bowler"
        elif bat_score > bowl_score:
            winner = "batsman"
        else:
            winner = "neutral"

        return {
            "winner": winner,
            "batsman_score": bat_score,
            "bowler_score": bowl_score,
            "reasons": reasons,
        }

    # ──────────────────────────────────────────
    # Main entry point
    # ──────────────────────────────────────────
    def generate_pvp_comparison(self, match_id: str, metadata: dict = None) -> dict:
        """
        Builds an optimized PvP comparison JSON for a given match.
        Filters for significance and prunes data to keep the file size robust.
        """
        match_id = str(match_id)

        try:
            squad_info = self._get_match_players(match_id)
        except Exception as e:
            return {"match_id": match_id, "error": str(e)}

        team_a, team_b = squad_info["team_a"], squad_info["team_b"]
        players_a, players_b = squad_info["players_a"], squad_info["players_b"]

        all_candidate_matchups = []

        # Helper to process matchups between a batting list and bowling list
        def _process_pool(batters, bowlers, bat_team, bowl_team, vs_team_name):
            for batter in batters:
                bat_career = self._get_career_batting(batter)
                bat_form = self._get_recent_form_batting(batter)
                vs_team_data = self._get_vs_team(batter, vs_team_name)

                for bowler in bowlers:
                    bowl_career = self._get_career_bowling(bowler)
                    bowl_form = self._get_recent_form_bowling(bowler)
                    h2h = self._get_h2h(batter, bowler)

                    # Significance Score for ranking
                    score = 0
                    if h2h["found"]:
                        score += (h2h["balls"] * 0.5) + (h2h["dismissals"] * 15)
                    if vs_team_data["found"]:
                        score += 10
                    
                    # Bonus for Star vs Star
                    if bat_career.get("average", 0) or 0 > 35: score += 5
                    if bowl_career.get("wickets", 0) or 0 > 50: score += 5

                    # Skip matchups with zero historical data unless star vs star
                    if not h2h["found"] and not vs_team_data["found"] and score < 15:
                        continue

                    verdict = self._generate_verdict(h2h, vs_team_data, bat_career, bowl_career)
                    
                    # Data Pruning: Remove 'found' flags and empty sections
                    m = {
                        "bat": batter, "bat_t": bat_team,
                        "bowl": bowler, "bowl_t": bowl_team,
                        "v": verdict["winner"]
                    }
                    if h2h["found"]:
                        m["h2h"] = {k: v for k, v in h2h.items() if k != "found"}
                    if vs_team_data["found"]:
                        m["vs_t"] = {k: v for k, v in vs_team_data.items() if k != "found"}
                    
                    # Simplified Careers
                    if bat_career["found"]:
                        m["b_car"] = {"avg": bat_career["average"], "sr": bat_career["strike_rate"]}
                    if bowl_career["found"]:
                        m["w_car"] = {"avg": bowl_career["average"], "eco": bowl_career["economy"]}

                    # Simplified Form (last 3 runs/wickets only)
                    if bat_form: m["b_f"] = [f["runs"] for f in bat_form]
                    if bowl_form: m["w_f"] = [f["wickets"] for f in bowl_form]
                    
                    m["_score"] = score # temporary for sorting
                    all_candidate_matchups.append(m)

        # Process both innings
        _process_pool(players_a, players_b, team_a, team_b, team_b)
        _process_pool(players_b, players_a, team_b, team_a, team_a)

        # Sort by significance and take top 50
        all_candidate_matchups.sort(key=lambda x: x["_score"], reverse=True)
        top_matchups = all_candidate_matchups[:50]
        
        # Clean up temporary score
        for m in top_matchups:
            if "_score" in m: del m["_score"]

        result = {
            "match_id": match_id,
            "team_a": team_a,
            "team_b": team_b,
            "matchups": top_matchups, # renamed from key_matchups for brevity
        }

        # Persist
        out_path = self.data_dir / "processed" / "t20" / "matches" / match_id / "pvp_comparison.json"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w") as f:
            json.dump(result, f, indent=2)

        return result



# ─────────────────────────────────────────────
# Standalone convenience function
# ─────────────────────────────────────────────
def calculate_pvp_comparison(match_id: str, data_dir: str = "d:/CricAI/data") -> dict:
    engine = PvPComparisonEngine(data_dir=data_dir)
    return engine.generate_pvp_comparison(match_id)
