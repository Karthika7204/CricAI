def detect_weakness(stats):

    if stats is None:
        return ["Player not found"]

    weaknesses = []

    # ----------------------------
    # Threshold configuration
    # ----------------------------

    THRESHOLDS = {
        "strike_rate": 110,
        "dot_ball_pct": 50,
        "boundary_pct": 10,
        "singles_pct": 15,
        "powerplay_sr": 110,
        "middle_sr": 105,
        "death_sr": 130
    }

    DISMISSAL_THRESHOLDS = {
        "caught": 40,
        "bowled": 20,
        "lbw": 15,
        "run out": 10
    }

    # ----------------------------
    # Extract stats safely
    # ----------------------------

    strike_rate = stats.get("strike_rate", 0)
    dot_ball_pct = stats.get("dot_ball_pct", 0)
    boundary_pct = stats.get("boundary_pct", 0)
    singles_pct = stats.get("singles_pct", 0)

    powerplay_sr = stats.get("powerplay_sr", 0)
    middle_sr = stats.get("middle_sr", 0)
    death_sr = stats.get("death_sr", 0)

    dismissal_types = stats.get("dismissal_types", {})
    bowler_dismissals = stats.get("bowler_dismissals", {})

    dot_pressure = stats.get("dot_pressure", False)
    boundary_dependency = stats.get("boundary_dependency", False)

    # ----------------------------
    # Core batting metrics
    # ----------------------------

    if strike_rate < THRESHOLDS["strike_rate"]:
        weaknesses.append("Low strike rate")

    if dot_ball_pct > THRESHOLDS["dot_ball_pct"]:
        weaknesses.append("Too many dot balls")

    if boundary_pct < THRESHOLDS["boundary_pct"]:
        weaknesses.append("Low boundary hitting ability")

    if singles_pct < THRESHOLDS["singles_pct"]:
        weaknesses.append("Poor strike rotation")

    if boundary_dependency:
        weaknesses.append("Over dependent on boundaries")

    if dot_pressure:
        weaknesses.append("High dot ball pressure")

    # ----------------------------
    # Phase of game analysis
    # ----------------------------

    if powerplay_sr < THRESHOLDS["powerplay_sr"]:
        weaknesses.append("Struggles in powerplay against new ball")

    if middle_sr < THRESHOLDS["middle_sr"]:
        weaknesses.append("Slow scoring in middle overs")

    if death_sr < THRESHOLDS["death_sr"]:
        weaknesses.append("Weak finishing ability in death overs")

    # ----------------------------
    # Dismissal pattern analysis
    # ----------------------------

    for dismissal_type, threshold in DISMISSAL_THRESHOLDS.items():

        count = dismissal_types.get(dismissal_type, 0)

        if count > threshold:

            if dismissal_type == "caught":
                weaknesses.append("Risky aerial shots leading to catches")

            elif dismissal_type == "bowled":
                weaknesses.append("Struggles against straight deliveries")

            elif dismissal_type == "lbw":
                weaknesses.append("Poor front foot judgement (LBW risk)")

            elif dismissal_type == "run out":
                weaknesses.append("Poor running between wickets")

    # ----------------------------
    # Line / length inference
    # ----------------------------

    caught = dismissal_types.get("caught", 0)
    lbw = dismissal_types.get("lbw", 0)
    bowled = dismissal_types.get("bowled", 0)

    if caught > 50:
        weaknesses.append("Chasing wide balls outside off stump")
        weaknesses.append("Falls into deep field traps")

    if lbw > 10:
        weaknesses.append("Vulnerable to straight line bowling")

    if bowled > 20:
        weaknesses.append("Difficulty handling yorkers and full balls")

    if caught > 45:
        weaknesses.append("Mistiming short balls")

    # ----------------------------
    # Bowler specific weakness
    # ----------------------------

    if bowler_dismissals:

        most_dangerous_bowler = max(
            bowler_dismissals,
            key=bowler_dismissals.get
        )

        dismissals = bowler_dismissals[most_dangerous_bowler]

        if dismissals >= 4:
            weaknesses.append(
                f"Repeated dismissals vs bowler {most_dangerous_bowler}"
            )

    # ----------------------------
    # Fallback
    # ----------------------------

    if not weaknesses:
        weaknesses.append("Strong overall performance")

    return list(set(weaknesses))