import json
import os

class FlowBuilder:
    """
    Deterministic extraction of tactical events from structured_summary.json.
    """
    def __init__(self, match_data_path):
        self.match_data_path = match_data_path
        self.summary_path = os.path.join(match_data_path, "structured_summary.json")
        self.data = self._load_data()

    def _load_data(self):
        norm_path = os.path.normpath(self.summary_path)
        if not os.path.exists(norm_path):
            return None
        with open(norm_path, 'r') as f:
            return json.load(f)

    def extract_events(self):
        if not self.data:
            return []

        events = []
        
        # 1. Powerplay Analysis
        for inning in self.data.get("Innings_Metrics", []):
            team = inning.get("team")
            pp = inning.get("phase_analysis", {}).get("Powerplay", {})
            if pp:
                events.append({
                    "phase": "Powerplay",
                    "team": team,
                    "type": "Phase Performance",
                    "description": f"{team} scored {pp.get('runs')} runs for {pp.get('wkts')} wickets in Powerplay (RR: {pp.get('rr')})."
                })

        # 2. Detailed Impact Analysis (Anchors & Special Spells)
        impact_analysis = self.data.get("Detailed_Impact_Analysis", [])
        for impact in impact_analysis:
            player = impact.get("player")
            role = impact.get("role")
            score = impact.get("score", 0)
            
            if role == "batting" and impact.get("win_contribution_percent", 0) >= 40:
                events.append({
                    "phase": "All",
                    "type": "Anchor Performance",
                    "impact_score": score,
                    "description": f"{player} anchored the innings with {impact.get('match_stats')}, contributing {impact.get('win_contribution_percent')}% of the total runs."
                })
            
            if role == "bowling":
                wickets = impact.get("wickets", 0)
                econ = impact.get("econ", 0)
                if wickets >= 3 or (econ <= 6 and impact.get("overs", 0) >= 3):
                    events.append({
                        "phase": "All",
                        "type": "Bowling Spell",
                        "impact_score": score,
                        "description": f"{player} delivered a crucial spell: {impact.get('match_stats')}."
                    })

        # 3. Collapse & Pressure Detection
        tactical = self.data.get("Tactical_Post_Match_Analysis", [])
        for note in tactical:
            events.append({
                "phase": "Tactical",
                "type": "Turning Point",
                "description": note
            })

        # 4. Result Summary
        result = self.data.get("Match_Result", {}).get("summary")
        if result:
            events.append({
                "phase": "Finish",
                "type": "Result",
                "description": result
            })

    def extract_summary_for_recommendations(self):
        """
        Extracts a condensed version of the structured summary for recommendation generation.
        """
        if not self.data:
            return ""

        summary = {
            "Match_Result": self.data.get("Match_Result"),
            "Innings_Metrics": self.data.get("Innings_Metrics"),
            "Tactical_Post_Match_Analysis": self.data.get("Tactical_Post_Match_Analysis"),
            "Bowling_Standouts": self.data.get("Scorecard_Highlights", {}).get("Bowling_Standouts"),
            "Significant_Collapses": self.data.get("Scorecard_Highlights", {}).get("Significant_Collapses")
        }

        # Handle top performers from impact analysis
        impact_analysis = self.data.get("Detailed_Impact_Analysis", [])
        top_performers = []
        for impact in impact_analysis:
            if impact.get("score", 0) > 80: # High impact threshold
                top_performers.append({
                    "player": impact.get("player"),
                    "team": impact.get("team"),
                    "role": impact.get("role"),
                    "stats": impact.get("match_stats"),
                    "impact_score": impact.get("score")
                })
        
        summary["Top_Impact_Performers"] = top_performers

        return json.dumps(summary, indent=2)
