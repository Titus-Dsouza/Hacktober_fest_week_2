import logging
import re

from . import ai
from .mission_rules import mission_category, mission_difficulty, safety_considerations
from .prompts import build_system_prompt

logger = logging.getLogger(__name__)

DEFAULT_DURATION_MINUTES = 30
MAX_DURATION_MINUTES = 120
NUMBER_WORDS = {
    "a": 1,
    "an": 1,
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
}


def _contains_any(message, terms):
    return any(re.search(rf"\b{re.escape(term)}\b", message) for term in terms)


def _extract_duration_minutes(message):
    numeric_match = re.search(
        r"\b(?P<amount>\d+(?:\.\d+)?)\s*(?P<unit>hours?|hrs?|h|minutes?|mins?|m)\b",
        message,
        re.IGNORECASE,
    )
    if numeric_match:
        amount = float(numeric_match.group("amount"))
        unit = numeric_match.group("unit").lower()
        minutes = amount * 60 if unit.startswith(("h", "hr")) else amount
        return min(MAX_DURATION_MINUTES, max(1, round(minutes)))

    if re.search(r"\bhalf\s+(?:an?\s+)?hour\b", message, re.IGNORECASE):
        return 30

    word_match = re.search(
        r"\b(?P<amount>a|an|one|two|three|four|five)\s+(?P<unit>hours?|hrs?|minutes?|mins?)\b",
        message,
        re.IGNORECASE,
    )
    if word_match:
        amount = NUMBER_WORDS[word_match.group("amount").lower()]
        unit = word_match.group("unit").lower()
        minutes = amount * 60 if unit.startswith(("h", "hr")) else amount
        return min(MAX_DURATION_MINUTES, max(1, minutes))

    return DEFAULT_DURATION_MINUTES


def _extract_context(message):
    normalized = message.lower()
    requested_minutes = _extract_duration_minutes(normalized)

    mood = "balanced"
    if _contains_any(
        normalized,
        ("relax", "relaxing", "relaxed", "calm", "stress", "stressed", "quiet", "slow", "rest", "peaceful", "reset", "unwind"),
    ):
        mood = "calm"
    elif _contains_any(
        normalized,
        ("explore", "exploring", "curious", "photo", "discover", "adventure", "wander", "hike", "hiking"),
    ):
        mood = "curious"
    elif _contains_any(
        normalized,
        ("run", "running", "jog", "jogging", "active", "exercise", "move", "energetic", "workout", "fitness", "cardio"),
    ):
        mood = "energetic"

    if _contains_any(
        normalized,
        (
            "tired",
            "low-energy",
            "low energy",
            "gentle",
            "easy",
            "relax",
            "relaxing",
            "relaxed",
            "calm",
            "stressed",
            "stress",
            "beginner",
        ),
    ):
        energy_level = "low"
    elif _contains_any(
        normalized,
        ("energetic", "high-energy", "high energy", "challenging", "difficult", "hard", "intense", "workout", "cardio"),
    ):
        energy_level = "high"
    else:
        energy_level = "moderate"

    mentions_indoor = _contains_any(normalized, ("indoor", "indoors", "inside", "stay in", "at home"))
    mentions_outdoor = _contains_any(normalized, ("outdoor", "outdoors", "outside", "park", "trail", "fresh air"))
    if mentions_indoor and not mentions_outdoor:
        setting_preference = "indoor"
    elif mentions_outdoor:
        setting_preference = "outdoor"
    else:
        setting_preference = "unspecified"

    if _contains_any(normalized, ("garden", "gardening", "plant", "plants", "watering")):
        activity_preference = "gardening_nature_care"
    elif _contains_any(normalized, ("friend", "friends", "social", "together", "someone")):
        activity_preference = "social_outdoors"
    elif _contains_any(
        normalized,
        ("bird", "birds", "nature", "observe", "observation", "wildlife", "listen for"),
    ):
        activity_preference = "nature_observation"
    elif _contains_any(normalized, ("mindful", "mindfulness", "meditate", "meditation", "breathing")):
        activity_preference = "relaxation_mindfulness"
    elif _contains_any(normalized, ("bike", "biking", "cycling", "cycle")):
        activity_preference = "cycling"
    elif _contains_any(normalized, ("run", "jog")):
        activity_preference = "running"
    elif _contains_any(normalized, ("running", "jogging")):
        activity_preference = "running"
    elif _contains_any(normalized, ("hike", "hiking")):
        activity_preference = "hiking"
    elif _contains_any(normalized, ("walk", "walking", "stroll")):
        activity_preference = "walking"
    else:
        activity_preference = "unspecified"

    constraints = []
    if _contains_any(normalized, ("wheelchair", "limited mobility", "mobility access", "avoid stairs", "flat route")):
        constraints.append("accessible_flat_route")
    if _contains_any(normalized, ("no equipment", "no gear", "nothing to bring", "without equipment")):
        constraints.append("no_equipment")
    if _contains_any(normalized, ("rain", "rainy", "wet weather")):
        constraints.append("shelter_from_weather")
    if _contains_any(normalized, ("near home", "nearby", "close by", "close to home")):
        constraints.append("nearby")
    if _contains_any(
        normalized,
        ("can't walk", "cannot walk", "unable to walk", "can't stand", "seated", "chair-based"),
    ):
        constraints.append("seated_or_stationary")

    duration_minutes = min(requested_minutes, 40) if mood == "calm" else requested_minutes
    difficulty_preference = (
        "challenging"
        if _contains_any(normalized, ("challenging", "difficult", "intense", "hard workout"))
        else "moderate"
        if _contains_any(normalized, ("moderate effort", "moderate difficulty", "moderate challenge"))
        else "unspecified"
    )
    return {
        "available_minutes": requested_minutes,
        "duration_minutes": duration_minutes,
        "mood": mood,
        "energy_level": energy_level,
        "setting_preference": setting_preference,
        "activity_preference": activity_preference,
        "constraints": constraints,
        "difficulty_preference": difficulty_preference,
    }


def _create_mission(context):
    sheltered = (
        context["setting_preference"] == "indoor"
        or "shelter_from_weather" in context["constraints"]
    )
    accessible = "accessible_flat_route" in context["constraints"]
    stationary = "seated_or_stationary" in context["constraints"]

    if stationary:
        title = "A stillness-and-noticing break"
        activity = (
            "Settle at a comfortable, accessible outdoor spot and notice the small "
            "details around you without needing to move."
        )
        instructions = [
            "Choose a familiar place to sit or pause that feels comfortable.",
            "Notice a nearby sound, a color, and the feel of the air.",
            "Stay only as long as feels good, then head back when you are ready.",
        ]
        challenge = "Notice one small detail you might usually pass by."
        setting = "sheltered_outdoors" if sheltered else "outdoors"
        bring = "No special equipment is needed."
    elif sheltered:
        title = "A sheltered fresh-air reset"
        activity = (
            "Find a covered porch, sheltered path, or another comfortable spot just outside "
            "and take an easy breath of fresh air."
        )
        instructions = [
            "Choose a nearby covered outdoor spot that feels comfortable and accessible.",
            "Spend a few minutes noticing the air, light, and sounds around you.",
            "If the weather or setting does not feel safe, postpone the mission until conditions improve.",
        ]
        challenge = "Notice one sound or detail you usually miss."
        setting = "sheltered_outdoors"
        bring = "No special equipment; a light layer if you need one."
    elif context["activity_preference"] == "cycling" and "no_equipment" not in context["constraints"]:
        title = "A neighborhood cycle"
        activity = (
            "Take an easy ride on a familiar route, keeping the pace comfortable and the "
            "route within your available time."
        )
        instructions = [
            "Choose a familiar route with safe places to pause.",
            "Ride at a comfortable pace and notice a few details along the way.",
            "Follow local road rules and turn back when your time is up.",
        ]
        challenge = "Pause somewhere safe and notice one thing you would miss from a car."
        setting = "outdoors"
        bring = "A road-safe bicycle and any safety gear you normally use."
    elif context["activity_preference"] == "hiking":
        title = "A nearby trail wander"
        activity = (
            "Choose a familiar, well-marked trail and enjoy a short hike at a comfortable pace."
        )
        instructions = [
            "Pick a familiar trail that fits your available time and current conditions.",
            "Stay on the marked path and pause whenever you like.",
            "Turn back with enough time to return safely before your time is up.",
        ]
        challenge = "Notice one small detail along the trail that you have not noticed before."
        setting = "outdoors"
        bring = "Comfortable footwear and water."
    elif context["activity_preference"] == "nature_observation":
        title = "The small wonders watch"
        activity = (
            "Find a nearby green or open space and quietly observe the plants, birds, "
            "clouds, or other details around you."
        )
        instructions = [
            "Choose a comfortable spot in a park, garden, campus, or nearby outdoor space.",
            "Spend a few minutes noticing colors, movement, or sounds without disturbing wildlife.",
            "Pick one detail to remember, then return whenever you are ready.",
        ]
        challenge = "Notice three things you had not paid attention to before."
        setting = "outdoors"
        bring = "Nothing beyond comfortable clothing; no special gear is needed."
    elif context["activity_preference"] == "gardening_nature_care":
        title = "A little garden care"
        activity = (
            "Spend a few easy minutes with a plant or garden you are allowed to care "
            "for, or simply notice how a nearby green space is growing."
        )
        instructions = [
            "Choose a garden or planter you have permission to tend, or a public green space to observe.",
            "Water or gently tidy one plant only if it is appropriate and supplies are already available.",
            "Pause to notice one sign of new growth, then leave the space as you found it.",
        ]
        challenge = "Find one small sign of growth or seasonal change."
        setting = "outdoors"
        bring = "No special equipment; use only supplies already available and permitted."
    elif context["activity_preference"] == "social_outdoors":
        title = "A fresh-air catch-up"
        activity = (
            "Invite someone for an easy chat in a nearby park, garden, campus, or other "
            "comfortable outdoor place. If plans do not line up, take a quiet pause there."
        )
        instructions = [
            "Choose a familiar, easy-to-reach outdoor place.",
            "Invite someone for a short conversation, or enjoy the surroundings on your own.",
            "Keep it relaxed and head back whenever you are ready.",
        ]
        challenge = "Share one good thing you noticed today."
        setting = "outdoors"
        bring = "Nothing special; bring water if you would like."
    elif context["activity_preference"] == "relaxation_mindfulness":
        title = "A mindful outside minute"
        activity = (
            "Find a comfortable outdoor spot and take a quiet pause, noticing your "
            "breathing, the light, and the sounds around you."
        )
        instructions = [
            "Choose a familiar place where you can comfortably pause.",
            "Take a few natural, unforced breaths and notice what you can hear.",
            "Finish whenever you feel ready; there is no pace or target to meet.",
        ]
        challenge = "Notice one sound, one color, and one comfortable sensation."
        setting = "outdoors"
        bring = "No special equipment is needed."
    elif context["activity_preference"] == "light_movement":
        title = "A gentle movement break"
        activity = (
            "Take a comfortable walk or try a few gentle stretches in a familiar outdoor "
            "space, choosing only what feels right for you."
        )
        instructions = [
            "Choose a familiar flat place with room to pause.",
            "Walk at an easy pace or do a gentle stretch if that feels comfortable.",
            "Stop or rest whenever you want and return at your own pace.",
        ]
        challenge = "Notice how the fresh air feels as you move or pause."
        setting = "outdoors"
        bring = "Comfortable clothing; no special equipment is needed."
    elif context["mood"] == "calm" or context["energy_level"] == "low":
        title = "The quiet reset"
        activity = (
            "Take a gentle walk somewhere with trees, fresh air, and room to breathe. "
            "Let the pace stay easy."
        )
        instructions = [
            "Choose a familiar nearby route with a comfortable place to pause.",
            "Walk at an easy pace and let your shoulders relax.",
            "Notice one sound you usually miss and one thing that feels lighter.",
        ]
        challenge = instructions[-1]
        setting = "outdoors"
        bring = "Comfortable shoes; no special gear is needed."
    elif context["mood"] == "curious":
        title = "The tiny-things expedition"
        activity = (
            "Explore a nearby street, path, or park as if it were somewhere new. "
            "Keep the route short and familiar."
        )
        instructions = [
            "Pick a nearby outdoor route that fits the time you have.",
            "Look for one surprising color, one interesting texture, and one thing in motion.",
            "Put your phone away for the walk and head back when your time is up.",
        ]
        challenge = instructions[1]
        setting = "outdoors"
        bring = "A curious eye; no special gear is needed."
    elif context["mood"] == "energetic" or context["energy_level"] == "high":
        title = "A change-of-pace loop"
        activity = (
            "Take a brisk walk on a familiar route. Add a short faster stretch only if it "
            "feels comfortable."
        )
        instructions = [
            "Choose a familiar, mostly flat route and start at a comfortable pace.",
            "Walk briskly for a short stretch, then slow down and catch your breath.",
            "Keep the effort comfortable and turn back whenever you need to.",
        ]
        challenge = "Finish with a minute of stillness and a deep breath."
        setting = "outdoors"
        bring = "Water and comfortable shoes."
    else:
        title = "The unhurried wander"
        activity = (
            "Take an easy walk somewhere with trees or open sky. There is no pace to keep "
            "and no destination to reach."
        )
        instructions = [
            "Choose a nearby outdoor route that fits the time you have.",
            "Walk at your own pace and notice three small things you usually pass by.",
            "Keep your phone away for a few minutes and turn back when you are ready.",
        ]
        challenge = instructions[1]
        setting = "outdoors"
        bring = "Comfortable shoes and a little curiosity."

    if accessible and not stationary:
        if sheltered:
            activity = (
                "Choose an accessible covered outdoor spot or a step-free sheltered route "
                "and take a gentle fresh-air pause."
            )
            instructions[0] = "Choose a familiar, step-free covered spot that feels comfortable."
            instructions[1] = "Pause or move at a comfortable pace and notice the air and sounds."
            setting = "sheltered_outdoors"
        elif context["activity_preference"] == "cycling":
            activity = (
                "If you have a suitable cycle, take an easy ride on a familiar, flat, step-free route. "
                "Otherwise, pause at an accessible outdoor spot and enjoy the fresh air."
            )
            instructions[0] = "Choose a familiar flat, step-free route suited to your mobility and equipment."
            instructions[1] = "Ride at a comfortable pace or pause at an accessible outdoor spot."
            setting = "outdoors"
        else:
            activity = (
                "Take an easy outing on a flat, step-free route, or settle at an accessible outdoor "
                "spot and notice what is around you."
            )
            instructions[0] = "Choose a familiar flat, step-free route or an accessible outdoor spot."
            instructions[1] = "Move or pause at a comfortable pace and notice the details around you."
            setting = "outdoors"

    duration_minutes = context["duration_minutes"]
    mission = {
        "title": title,
        "duration": f"{duration_minutes} minutes",
        "duration_minutes": duration_minutes,
        "activity": activity,
        "instructions": instructions,
        "description": activity,
        "challenge": challenge,
        "bring": bring,
        "setting": setting,
        "energy_level": context["energy_level"],
        "type": "outdoor_mission",
    }
    mission.update(
        {
            "category": mission_category(context),
            "difficulty": mission_difficulty(context),
            "safety_considerations": safety_considerations(
                context, setting, context["activity_preference"]
            ),
        }
    )
    return mission


def create_outdoor_mission(message):
    if not isinstance(message, str) or not message.strip():
        raise ValueError("A non-empty message is required.")
    return _create_mission(_extract_context(" ".join(message.split())))


def _build_reply(mission):
    if mission["setting"] == "sheltered_outdoors":
        return "I found a gentle fresh-air option with some shelter."
    if mission["energy_level"] == "low":
        return "I picked a low-pressure mission to help you slow down outside."
    if mission["energy_level"] == "high":
        return "I picked a comfortable way to get moving outdoors."
    if mission["title"] == "The tiny-things expedition":
        return "I picked a curious little mission to help you notice your surroundings."
    return "Here's a little outside mission picked for you."


def generate_chat_response(message):
    if not isinstance(message, str) or not message.strip():
        raise ValueError("A non-empty message is required.")

    normalized_message = " ".join(message.split())
    context = _extract_context(normalized_message)

    if ai.ai_enabled():
        try:
            mission = ai.generate_ai_mission(normalized_message, context)
        except ai.AIError as exc:
            logger.warning(
                "Open-weight model unavailable or returned invalid output; "
                "falling back to the rule-based generator: %s",
                exc,
            )
        else:
            mission["energy_level"] = context["energy_level"]
            mission["category"] = mission_category(context, mission["category"])
            mission["difficulty"] = mission_difficulty(context, mission["difficulty"])
            mission["safety_considerations"] = safety_considerations(
                context, mission["setting"], context["activity_preference"]
            )
            return {"reply": _build_reply(mission), "mission": mission}

    mission = _create_mission(context)
    return {"reply": _build_reply(mission), "mission": mission}


def get_system_prompt():
    return build_system_prompt()
