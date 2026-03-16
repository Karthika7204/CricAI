def predict_field_setup(weaknesses):

    field_positions = []

    for w in weaknesses:

        w = w.lower()

        if "caught" in w or "aerial" in w:
            field_positions = [
                "Slip",
                "Gully",
                "Point",
                "Deep Cover",
                "Long Off"
            ]

        elif "short ball" in w:
            field_positions = [
                "Deep Square Leg",
                "Fine Leg",
                "Long Leg",
                "Mid Wicket"
            ]

        elif "lbw" in w:
            field_positions = [
                "Short Mid Wicket",
                "Mid On",
                "Square Leg",
                "Fine Leg"
            ]

        elif "dot ball" in w:
            field_positions = [
                "Point",
                "Cover",
                "Mid Off",
                "Mid On"
            ]

    if not field_positions:
        field_positions = [
            "Slip",
            "Point",
            "Cover",
            "Mid Off",
            "Mid On"
        ]

    return field_positions