MISSION_CATEGORIES = (
    "walking_exploring",
    "nature_observation",
    "relaxation_mindfulness",
    "light_movement",
    "gardening_nature_care",
    "social_outdoors",
)
DIFFICULTY_LEVELS = ("Easy", "Moderate", "Challenging")


def mission_category(context, suggested=None):
    preference = context.get("activity_preference", "unspecified")
    if preference in MISSION_CATEGORIES:
        return preference
    if "seated_or_stationary" in context.get("constraints", []):
        return "relaxation_mindfulness"
    if preference in {"cycling", "running", "hiking"}:
        return "light_movement"
    if suggested in MISSION_CATEGORIES:
        return suggested
    if context.get("mood") == "calm" or context.get("energy_level") == "low":
        return "relaxation_mindfulness"
    if context.get("mood") == "energetic" or context.get("energy_level") == "high":
        return "light_movement"
    return "walking_exploring"


def mission_difficulty(context, suggested=None):
    energy = context.get("energy_level", "moderate")
    maximum = (
        "Challenging"
        if energy == "high" and context.get("difficulty_preference") == "challenging"
        else "Moderate"
        if energy == "high" or context.get("difficulty_preference") == "moderate"
        else "Easy"
    )
    if suggested not in DIFFICULTY_LEVELS:
        return maximum
    rank = {"Easy": 1, "Moderate": 2, "Challenging": 3}
    return min((suggested, maximum), key=rank.get)


def safety_considerations(context, setting, activity_preference):
    constraints = context.get("constraints", [])
    if "seated_or_stationary" in constraints:
        return (
            "Choose a comfortable, accessible place, stay within what feels right for "
            "you, and leave if the conditions feel uncomfortable."
        )
    if activity_preference == "cycling":
        return (
            "Use a road-safe bike and helmet, follow local traffic rules, and choose a "
            "familiar route; stop if conditions feel unsafe."
        )
    if "accessible_flat_route" in constraints:
        return (
            "Choose a familiar, step-free place that works for your mobility and current "
            "conditions; stop if anything feels uncomfortable."
        )
    if setting == "sheltered_outdoors":
        return (
            "Use a comfortable covered outdoor spot, check current conditions, and "
            "postpone if it does not feel safe."
        )
    return (
        "Choose a familiar place, follow local guidance and current conditions, and "
        "stop or head home if you feel uncomfortable."
    )
