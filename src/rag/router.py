import re


class Router:
    """
    Improved Rule-Based Router for deterministic fact queries.
    Avoids false triggering on player-level analytical questions.
    """

    def __init__(self, metadata):
        self.meta = metadata

        # Preload player names if available
        self.players = [
            p.lower() for p in metadata.get("all_players", [])
        ]

        # Strict match-level patterns only
        self.patterns = {
            "winner": r"\b(who won|which team won|match result|match winner)\b",
            "score": r"\b(final score|total score|team score|match score)\b",
            "margin": r"\b(won by \d+|margin of victory|victory margin)\b",
            "venue": r"\b(where was it played|match venue|stadium name)\b",
            "date": r"\b(match date|played on|when was the match)\b",
            "toss": r"\b(who won the toss|toss winner)\b",
            "captains": r"\b(team captain|who captained|captain of)\b",
            "match_flow": r"\b(match flow|how did the match progress|sequence of events|chronological flow)\b",
            "recommendations": r"\b(recommend|tactical suggestion|how can .* improve|what should .* do better|strategic adjustment|risk alert)\b",
            "pre_match_insights": r"\b(pre.match|insight|ranking race|milestone|upcoming milestone|career achievement|personal best|storyline)\b",
            "awards": (
                r"\b("
                r"awards?|player of (the )?match|man of (the )?match|potm|motm|"
                r"best bat(ter|sman|ting)?|best bowl(er|ing)?|"
                r"game.?changer|pressure performer|pressure player|"
                r"emerging player|young performer|rising star|"
                r"fielding (award|impact|hero)|best fielder|"
                r"all.?rounder (award|impact|of the match)|"
                r"who (won|got|received|deserved) the award|"
                r"top performer|star of the match"
                r")\b"
            )
        }

    # ------------------------------------------
    # Helper: Detect Player Mention
    # ------------------------------------------
    def contains_player_name(self, query):
        query = query.lower()
        return any(player in query for player in self.players)

    # ------------------------------------------
    # Main Router
    # ------------------------------------------
    def route(self, query):
        original_query = query
        query = query.lower()

        # 0️⃣ Awards — HIGHEST PRIORITY (deterministic fast track)
        if re.search(self.patterns.get("awards", ""), query, re.IGNORECASE):
            return "ROUTE_TO_AWARDS"

        # 0️⃣ Match Analysis (Flow & Recommendations) - HIGH PRIORITY specialized RAG
        if re.search(self.patterns.get("match_flow", ""), query):
            return "ROUTE_TO_ANALYSIS_FLOW"
            
        if re.search(self.patterns.get("recommendations", ""), query):
            return "ROUTE_TO_ANALYSIS_RECOMMEND"

        if re.search(self.patterns.get("pre_match_insights", ""), query):
            return "ROUTE_TO_PRE_MATCH_INSIGHTS"

        # -------------------------------------------------
        # 1️⃣ Block analytical / comparison questions
        # -------------------------------------------------
        analytical_patterns = [
            r"\bwas .* match winner\b",     # was X the match winner
            r"\bor just\b",                 # comparison phrase
            r"\bimpact\b",
            r"\bperformance\b",
            r"\bcontributor\b",
            r"\bhow did\b",
            r"\bwhy did\b",
            r"\bmatch flow\b",
            r"\brecommendation\b",
            r"\btactical\b"
        ]

        for pattern in analytical_patterns:
            if re.search(pattern, query):
                return None   # Force RAG

        # -------------------------------------------------
        # 2️⃣ Detect Proper Name (Capitalized Player Pattern)
        # Example: SA Yadav, Mohammed Siraj
        # -------------------------------------------------
        if re.search(r"\b[A-Z][a-z]+(?:\s[A-Z][a-z]+)+\b", original_query):
            return None  # Player detected → use RAG

        # -------------------------------------------------
        # 3️⃣ Strict Match Winner Only
        # -------------------------------------------------
        if re.search(r"\bwho won\b|\bwhich team won\b|\bmatch result\b", query):
            return f"The winner of the match was {self.meta['winner']}."

        # -------------------------------------------------
        # 4️⃣ Score Query
        # -------------------------------------------------
        if re.search(r"\bfinal score\b|\btotal score\b|\bmatch score\b", query):
            return f"Final Score: {self.meta['score']}."

        # -------------------------------------------------
        # 5️⃣ Margin
        # -------------------------------------------------
        if re.search(r"\bmargin of victory\b|\bwon by\b", query):
            return f"The match was decided by {self.meta['margin']} {self.meta['margin_type']}."

        # -------------------------------------------------
        # 6️⃣ Venue
        # -------------------------------------------------
        if re.search(r"\bvenue\b|\bstadium\b|\bwhere was it played\b", query):
            return f"The match was played at {self.meta['venue']}."

        # -------------------------------------------------
        # 7️⃣ Date
        # -------------------------------------------------
        if re.search(r"\bmatch date\b|\bplayed on\b|\bwhen was the match\b", query):
            return f"The match took place on {self.meta['date']}."

        # -------------------------------------------------
        # 8️⃣ Toss
        # -------------------------------------------------
        if re.search(r"\btoss winner\b|\bwho won the toss\b", query):
            return f"The toss was won by {self.meta['toss_winner']}."

        # -------------------------------------------------
        # Default → RAG
        # -------------------------------------------------
        return None