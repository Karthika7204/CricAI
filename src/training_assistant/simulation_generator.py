def generate_training_plan(player_name, stats, weaknesses):

    weakness_map = {

        "dot ball": {
            "training": [
                "Strike rotation drills",
                "Quick single running practice",
                "Soft hands deflection practice"
            ],
            "tips": [
                "Reduce dot ball pressure by rotating strike"
            ]
        },

        "boundary": {
            "training": [
                "Power hitting drills",
                "Range hitting practice",
                "Bat speed improvement"
            ],
            "tips": [
                "Improve bat swing and hitting zones"
            ]
        },

        "pace": {
            "training": [
                "Fast bowling machine drills",
                "Reaction time training",
                "Back-foot defense drills"
            ],
            "tips": [
                "Practice against 140+ km/h deliveries"
            ]
        },

        "spin": {
            "training": [
                "Footwork against spin drills",
                "Sweep shot practice",
                "Use crease vs spin"
            ],
            "tips": [
                "Read spin from bowler's hand"
            ]
        },

        "short ball": {
            "training": [
                "Pull shot practice",
                "Hook shot drills",
                "Short ball reaction training"
            ],
            "tips": [
                "Maintain back-foot balance"
            ]
        },

        "yorker": {
            "training": [
                "Yorker defense drills",
                "Toe-end bat control practice",
                "Late bat swing drills"
            ],
            "tips": [
                "Practice digging out yorkers"
            ]
        },

        "swing": {
            "training": [
                "Playing late against swing",
                "Off stump awareness drills",
                "Leave ball judgment"
            ],
            "tips": [
                "Avoid chasing balls outside off stump"
            ]
        }
    }

    field_map = {

        "caught": [
            "Slip",
            "Gully",
            "Point",
            "Deep cover",
            "Long off"
        ],

        "lbw": [
            "Short midwicket",
            "Mid on",
            "Mid off",
            "Square leg",
            "Fine leg"
        ],

        "short ball": [
            "Deep square leg",
            "Fine leg",
            "Deep midwicket"
        ],

        "spin": [
            "Slip",
            "Short leg",
            "Deep midwicket",
            "Long on"
        ]
    }

    training_plan = set()
    training_tips = set()
    field_setup = set()

    for weakness in weaknesses:

        w = weakness.lower()

        # Training plan detection
        for key in weakness_map:
            if key in w:
                training_plan.update(weakness_map[key]["training"])
                training_tips.update(weakness_map[key]["tips"])

        # Field setup detection
        for key in field_map:
            if key in w:
                field_setup.update(field_map[key])

    # fallback
    if not training_plan:
        training_plan.update([
            "General batting consistency drills",
            "Match simulation practice"
        ])

        training_tips.add(
            "Maintain performance and improve situational awareness"
        )

    return {
        "player": player_name,
        "weaknesses": weaknesses,
        "training_plan": list(training_plan),
        "field_setup_plan": list(field_setup),
        "training_tips": list(training_tips)
    }