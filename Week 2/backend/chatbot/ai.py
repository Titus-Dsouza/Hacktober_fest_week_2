"""Open-weight AI integration for the TouchGrass chatbot (Phase 6).

This module is the only place that knows about the local model server. It:

- builds the request to a local Ollama instance running an open-weight model,
- parses the model's structured JSON reply,
- normalizes and validates it against the existing mission serializer, and
- raises :class:`AIError` on *any* failure (missing model, network error,
  timeout, or invalid output) so ``services.py`` can fall back to the
  rule-based mission generator.

Configuration comes from Django settings (populated from environment variables
in ``config/settings.py``), so the model or provider can be replaced later
without touching the Django view or the frontend API contract.
"""

import json
import logging
import math
import re
import urllib.error
import urllib.request

from django.conf import settings

from .mission_rules import (
    DIFFICULTY_LEVELS,
    MISSION_CATEGORIES,
    mission_category,
    mission_difficulty,
    safety_considerations,
)
from .prompts import build_mission_json_prompt, build_system_prompt
from .serializers import OutdoorMissionSerializer

logger = logging.getLogger(__name__)

# Providers that explicitly turn the model off in favor of the rules.
DISABLED_PROVIDERS = {"", "none", "off", "disabled", "rule_based", "rules"}

DEFAULT_DURATION_MINUTES = 30
MIN_DURATION_MINUTES = 1
MAX_DURATION_MINUTES = 120

SETTING_MAP = {
    "outdoor": "outdoors",
    "outdoors": "outdoors",
    "outside": "outdoors",
    "open_air": "outdoors",
    "sheltered": "sheltered_outdoors",
    "sheltered_outdoor": "sheltered_outdoors",
    "sheltered_outdoors": "sheltered_outdoors",
    "indoor": "sheltered_outdoors",
    "indoors": "sheltered_outdoors",
    "covered": "sheltered_outdoors",
}

ENERGY_MAP = {
    "low": "low",
    "moderate": "moderate",
    "medium": "moderate",
    "normal": "moderate",
    "high": "high",
}

DIFFICULTY_MAP = {
    "easy": "Easy",
    "moderate": "Moderate",
    "challenging": "Challenging",
}


class AIError(Exception):
    """Raised when the open-weight model cannot produce a valid mission."""


def get_ai_config():
    """Return the AI configuration as a plain dict (read from settings)."""
    return {
        "provider": str(getattr(settings, "AI_PROVIDER", "ollama")).strip().lower(),
        "model": str(getattr(settings, "AI_MODEL", "")).strip(),
        "base_url": str(
            getattr(settings, "AI_BASE_URL", "http://127.0.0.1:11434")
        )
        .strip()
        .rstrip("/"),
        "timeout": float(getattr(settings, "AI_TIMEOUT_SECONDS", 10)),
    }


def get_provider():
    """Return a model provider instance, or ``None`` when AI is disabled."""
    config = get_ai_config()
    provider = config["provider"]
    if provider in DISABLED_PROVIDERS:
        return None
    if provider == "ollama":
        return OllamaProvider(
            base_url=config["base_url"],
            model=config["model"],
            timeout=config["timeout"],
        )
    logger.warning(
        "Unknown AI_PROVIDER %r configured; using the rule-based generator.",
        provider,
    )
    return None


def ai_enabled():
    """True when a usable open-weight provider is configured."""
    return get_provider() is not None


def _post_json(url, payload, timeout):
    """POST a JSON payload and return the decoded JSON response body."""
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raise AIError(f"The model server returned HTTP {exc.code}.") from exc
    except urllib.error.URLError as exc:
        raise AIError("Could not reach the model server.") from exc
    except TimeoutError as exc:
        raise AIError("The model server timed out.") from exc
    except json.JSONDecodeError as exc:
        raise AIError("The model server returned invalid JSON.") from exc
    except OSError as exc:
        raise AIError("Model server request failed.") from exc


class OllamaProvider:
    """Calls a local Ollama server (``POST /api/chat``) with JSON output mode."""

    def __init__(self, base_url, model, timeout):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout

    def generate(self, system_prompt, user_prompt):
        if not self.model:
            raise AIError("AI_MODEL is not configured.")
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "stream": False,
            "format": "json",
            "options": {"temperature": 0.6, "num_predict": 400},
        }
        data = self._post(payload)
        try:
            content = data["message"]["content"]
        except (KeyError, TypeError) as exc:
            raise AIError("The model response did not contain a message.") from exc
        if not isinstance(content, str) or not content.strip():
            raise AIError("The model returned an empty response.")
        return content

    def _post(self, payload):
        try:
            return _post_json(
                f"{self.base_url}/api/chat", payload, self.timeout
            )
        except AIError:
            raise
        except OSError as exc:
            # Covers transport failures (URLError, timeouts) so callers always
            # see AIError and can fall back to the rule-based generator.
            raise AIError("Model server request failed.") from exc


def _unwrap_payload(parsed):
    if isinstance(parsed, list):
        parsed = next((item for item in parsed if isinstance(item, dict)), None)
        if parsed is None:
            raise AIError("The model response did not contain a mission object.")
    if not isinstance(parsed, dict):
        raise AIError("The model response was not a JSON object.")
    mission = parsed.get("mission")
    if isinstance(mission, dict):
        return mission
    return parsed


def _parse_model_json(content):
    """Extract a JSON object from raw model output (tolerating fences/prose)."""
    if not isinstance(content, str) or not content.strip():
        raise AIError("The model returned an empty response.")
    text = content.strip()
    candidates = [text]
    fenced = re.search(r"```(?:json)?\s*(.*?)```", text, re.DOTALL | re.IGNORECASE)
    if fenced:
        candidates.append(fenced.group(1).strip())
    start, end = text.find("{"), text.rfind("}")
    if start != -1 and end > start:
        candidates.append(text[start : end + 1])
    for candidate in candidates:
        try:
            return _unwrap_payload(json.loads(candidate))
        except (json.JSONDecodeError, TypeError):
            continue
    raise AIError("The model did not return valid JSON.")


def _require_text(raw, key):
    value = raw.get(key)
    if not isinstance(value, str) or not value.strip():
        raise AIError(f"The model mission is missing a valid '{key}'.")
    return value.strip()


def _coerce_minutes(value):
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            return None
        return int(round(value))
    if isinstance(value, str):
        match = re.search(r"\d+(?:\.\d+)?", value)
        if match:
            return int(round(float(match.group(0))))
    return None


def _normalize_setting(value):
    if not isinstance(value, str):
        raise AIError("The model mission is missing 'setting'.")
    mapped = SETTING_MAP.get(value.strip().lower())
    if mapped is None:
        raise AIError("The model mission has an unknown setting.")
    return mapped


def _normalize_energy(value):
    if not isinstance(value, str):
        raise AIError("The model mission is missing 'energy_level'.")
    mapped = ENERGY_MAP.get(value.strip().lower())
    if mapped is None:
        raise AIError("The model mission has an unknown energy level.")
    return mapped


def _normalize_category(value):
    if value is None:
        return None
    if not isinstance(value, str) or value.strip().lower() not in MISSION_CATEGORIES:
        raise AIError("The model mission has an unknown activity category.")
    return value.strip().lower()


def _normalize_difficulty(value):
    if value is None:
        return None
    if not isinstance(value, str):
        raise AIError("The model mission has an invalid difficulty.")
    mapped = DIFFICULTY_MAP.get(value.strip().lower())
    if mapped is None:
        raise AIError("The model mission has an unknown difficulty.")
    return mapped


def _default_safety(context, setting):
    constraints = context.get("constraints", []) if isinstance(context, dict) else []
    details = dict(context or {})
    details["constraints"] = constraints
    return safety_considerations(
        details, setting, details.get("activity_preference", "unspecified")
    )


def normalize_mission(raw, context=None):
    """Convert a parsed model payload into a frontend-compatible mission.

    Raises :class:`AIError` if the payload cannot be trusted, so callers can
    fall back to the rule-based generator instead of returning bad data.
    """
    if not isinstance(raw, dict):
        raise AIError("The model mission was not a JSON object.")

    title = _require_text(raw, "title")
    activity = _require_text(raw, "activity")
    challenge = _require_text(raw, "challenge")
    bring = _require_text(raw, "bring")

    instructions = raw.get("instructions")
    if not isinstance(instructions, (list, tuple)):
        raise AIError("The model mission needs a list of instructions.")
    steps = [
        str(step).strip()
        for step in instructions
        if isinstance(step, str) and step.strip()
    ]
    if len(steps) < 3:
        raise AIError("The model mission needs at least three instructions.")

    default_minutes = DEFAULT_DURATION_MINUTES
    time_limit = DEFAULT_DURATION_MINUTES
    if isinstance(context, dict):
        value = context.get("duration_minutes") or context.get("available_minutes")
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            time_limit = max(MIN_DURATION_MINUTES, min(MAX_DURATION_MINUTES, int(value)))
            default_minutes = time_limit
    minutes = _coerce_minutes(raw.get("duration_minutes"))
    if minutes is None:
        minutes = _coerce_minutes(raw.get("duration"))
    if minutes is None:
        minutes = default_minutes
    minutes = max(
        MIN_DURATION_MINUTES,
        min(MAX_DURATION_MINUTES, time_limit, minutes),
    )

    suggested_category = _normalize_category(raw.get("category"))
    suggested_difficulty = _normalize_difficulty(raw.get("difficulty"))
    suggested_energy = (
        _normalize_energy(raw["energy_level"]) if "energy_level" in raw else None
    )
    suggested_safety = raw.get("safety_considerations")
    if suggested_safety is not None and (
        not isinstance(suggested_safety, str) or not suggested_safety.strip()
    ):
        raise AIError("The model mission has invalid safety considerations.")

    constraints = context.get("constraints", []) if isinstance(context, dict) else []
    requested_setting = raw.get("setting")
    if requested_setting is None:
        requested_setting = (
            "sheltered_outdoors"
            if isinstance(context, dict)
            and (
                context.get("setting_preference") == "indoor"
                or "shelter_from_weather" in constraints
            )
            else "outdoors"
        )
    setting = _normalize_setting(requested_setting)
    if isinstance(context, dict) and (
        context.get("setting_preference") == "indoor"
        or "shelter_from_weather" in constraints
    ):
        if setting != "sheltered_outdoors":
            raise AIError("The model mission did not respect the sheltered setting.")
    combined_text = " ".join(
        [title, activity, challenge, bring, *steps]
    ).lower()
    if re.search(
        r"\b(swim|swimming|climb|climbing|trespass|off[- ]trail|feed wildlife|approach wildlife)\b",
        combined_text,
    ):
        raise AIError("The model mission did not meet the application's safety rules.")
    if "accessible_flat_route" in constraints and re.search(
        r"\b(stairs?|staircase|steep|off[- ]trail)\b", combined_text
    ):
        raise AIError("The model mission did not respect the accessible route constraint.")
    if "no_equipment" in constraints and re.search(
        r"\b(?:bring|use|using|requires?|need)\s+(?:a|an|your|some)?\s*"
        r"(?:bicycle|bike|helmet|equipment|gear|mat|weights?)\b",
        combined_text,
    ):
        raise AIError("The model mission did not respect the no-equipment constraint.")
    if "seated_or_stationary" in constraints and re.search(
        r"\b(walk|walking|run|running|jog|jogging|cycle|cycling|hike|hiking|stairs?|climb)\b",
        combined_text,
    ):
        raise AIError("The model mission did not respect the user's movement constraint.")

    mission = {
        "title": title,
        "duration": f"{minutes} minutes",
        "duration_minutes": minutes,
        "activity": activity,
        "instructions": steps[:3],
        "description": activity,
        "challenge": challenge,
        "bring": bring,
        "setting": setting,
        "energy_level": (
            context.get("energy_level")
            if isinstance(context, dict)
            and context.get("energy_level") in {"low", "moderate", "high"}
            else suggested_energy or "moderate"
        ),
        "category": mission_category(context or {}, suggested_category),
        "difficulty": mission_difficulty(context or {}, suggested_difficulty),
        "safety_considerations": _default_safety(context, setting),
        "type": "outdoor_mission",
    }
    serializer = OutdoorMissionSerializer(data=mission)
    if not serializer.is_valid():
        raise AIError(f"The model mission failed validation: {serializer.errors}")
    return serializer.validated_data


def generate_ai_mission(message, context=None):
    """Ask the open-weight model for a mission; return a validated mission dict.

    Raises :class:`AIError` on any failure — callers must fall back to the
    rule-based generator.
    """
    provider = get_provider()
    if provider is None:
        raise AIError("No open-weight AI provider is configured.")

    try:
        content = provider.generate(
            build_system_prompt(),
            build_mission_json_prompt(message, context),
        )
    except AIError:
        raise
    except Exception as exc:  # pragma: no cover - defensive
        logger.error(
            "Unexpected open-weight model failure (%s).",
            type(exc).__name__,
        )
        raise AIError("Open-weight model request failed.") from exc

    return normalize_mission(_parse_model_json(content), context)
