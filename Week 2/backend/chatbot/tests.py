import json
import urllib.error
from unittest.mock import patch

from django.test import SimpleTestCase, override_settings
from rest_framework.test import APIClient

from chatbot import ai
from chatbot.serializers import OutdoorMissionSerializer
from chatbot.services import create_outdoor_mission, generate_chat_response, get_system_prompt
from users.authentication import SupabaseUser

VALID_AI_MISSION = {
    "title": "A riverside breath break",
    "duration_minutes": 45,
    "activity": "Walk to a nearby green space and notice the water, trees, and sky.",
    "instructions": [
        "Pick a nearby park or green space you can reach on foot.",
        "Walk at a relaxed pace with your phone away.",
        "Turn back with enough time to get home before your time is up.",
    ],
    "challenge": "Stand still for one full minute and just listen.",
    "bring": "Comfortable shoes and water.",
    "setting": "outdoors",
    "energy_level": "moderate",
}


def ai_response(content):
    return {"message": {"content": content}}


@override_settings(ALLOWED_HOSTS=["testserver"], AI_PROVIDER="rule_based")
class ChatApiTests(SimpleTestCase):
    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(
            user=SupabaseUser(id="verified-user-id", email="outside@example.com")
        )

    def test_chat_rejects_anonymous_request(self):
        response = APIClient().post(
            "/api/chat/",
            {"message": "A short walk, please"},
            format="json",
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data["error"]["code"], "authentication_required")

    def test_chat_returns_structured_mission_and_legacy_frontend_fields(self):
        response = self.client.post(
            "/api/chat/",
            {"message": "I have 45 minutes and want to explore"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        mission = response.data["mission"]
        self.assertEqual(response.data["reply"], "I picked a curious little mission to help you notice your surroundings.")
        self.assertEqual(mission["title"], "The tiny-things expedition")
        self.assertEqual(mission["duration"], "45 minutes")
        self.assertEqual(mission["duration_minutes"], 45)
        self.assertEqual(len(mission["instructions"]), 3)
        self.assertEqual(mission["description"], mission["activity"])
        self.assertIn("challenge", mission)
        self.assertIn("bring", mission)
        self.assertIn("category", mission)
        self.assertIn(mission["difficulty"], ("Easy", "Moderate", "Challenging"))
        self.assertTrue(mission["safety_considerations"])
        self.assertEqual(mission["type"], "outdoor_mission")

    def test_chat_uses_available_time_and_calm_mood(self):
        response = self.client.post(
            "/api/chat/",
            {"message": "I have one hour and want something relaxing"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        mission = response.data["mission"]
        self.assertEqual(mission["duration_minutes"], 40)
        self.assertEqual(mission["energy_level"], "low")
        self.assertEqual(mission["title"], "The quiet reset")

    def test_chat_uses_explicit_high_energy_preference(self):
        response = self.client.post(
            "/api/chat/",
            {"message": "I have 25 minutes and want something high energy"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["mission"]["energy_level"], "high")
        self.assertEqual(response.data["mission"]["title"], "A change-of-pace loop")

    def test_chat_handles_indoor_preference_with_sheltered_outdoor_mission(self):
        response = self.client.post(
            "/api/chat/",
            {"message": "I have 20 minutes and would prefer something indoors"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["mission"]["setting"], "sheltered_outdoors")
        self.assertIn("covered", response.data["mission"]["instructions"][0])

    def test_chat_uses_activity_and_accessibility_preferences(self):
        mission = create_outdoor_mission(
            "I have 30 minutes and want an accessible bike ride; avoid stairs"
        )
        self.assertEqual(mission["setting"], "outdoors")
        self.assertEqual(mission["title"], "A neighborhood cycle")
        self.assertIn("step-free", mission["activity"])
        self.assertIn("Choose a familiar flat", mission["instructions"][0])
        self.assertEqual(mission["category"], "light_movement")

    def test_chat_supports_nature_gardening_social_and_mindful_missions(self):
        cases = (
            ("I want to watch birds outside", "nature_observation"),
            ("I'd like to do some gardening", "gardening_nature_care"),
            ("I want to go outside with a friend", "social_outdoors"),
            ("I want a mindful breathing break", "relaxation_mindfulness"),
        )
        for message, expected_category in cases:
            with self.subTest(category=expected_category):
                mission = create_outdoor_mission(message)
                self.assertEqual(mission["category"], expected_category)
                self.assertEqual(len(mission["instructions"]), 3)

    def test_chat_uses_safe_stationary_option_for_movement_constraint(self):
        mission = create_outdoor_mission(
            "I have 15 minutes but cannot walk; I want to sit outside"
        )
        self.assertIn("without needing to move", mission["activity"])
        self.assertEqual(mission["duration_minutes"], 15)
        self.assertIn("accessible", mission["safety_considerations"])

    def test_incomplete_preferences_use_sensible_defaults(self):
        mission = create_outdoor_mission("I'd like a little fresh air")
        self.assertEqual(mission["duration_minutes"], 30)
        self.assertEqual(mission["category"], "walking_exploring")
        self.assertEqual(mission["difficulty"], "Easy")
        self.assertEqual(mission["setting"], "outdoors")

    def test_short_time_is_not_increased_to_the_old_ten_minute_minimum(self):
        mission = create_outdoor_mission("I have 5 minutes and low energy")
        self.assertEqual(mission["duration_minutes"], 5)

    def test_only_high_energy_explicit_challenge_gets_challenging_difficulty(self):
        challenging = create_outdoor_mission(
            "I have 25 minutes, high energy, and want a challenging activity"
        )
        ordinary = create_outdoor_mission("I have 25 minutes and high energy")
        low_energy = create_outdoor_mission(
            "I have 25 minutes, low energy, and want a challenging activity"
        )
        self.assertEqual(challenging["difficulty"], "Challenging")
        self.assertEqual(ordinary["difficulty"], "Moderate")
        self.assertEqual(low_energy["difficulty"], "Easy")

    def test_chat_rejects_client_supplied_conversation_history(self):
        response = self.client.post(
            "/api/chat/",
            {"message": "I have 20 minutes and want to walk", "history": []},
            format="json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["error"]["code"], "validation_error")

    def test_chat_rejects_blank_message(self):
        response = self.client.post("/api/chat/", {"message": "  "}, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["error"]["code"], "validation_error")

    def test_chat_rejects_missing_and_wrong_type_message(self):
        missing = self.client.post("/api/chat/", {}, format="json")
        wrong_type = self.client.post(
            "/api/chat/",
            {"message": ["a", "list"]},
            format="json",
        )
        for response in (missing, wrong_type):
            with self.subTest(status=response.status_code):
                self.assertEqual(response.status_code, 400)
                self.assertEqual(response.data["error"]["code"], "validation_error")

    def test_chat_rejects_message_over_limit(self):
        response = self.client.post("/api/chat/", {"message": "a" * 401}, format="json")
        self.assertEqual(response.status_code, 400)

    def test_chat_returns_standard_error_for_invalid_service_response(self):
        with patch(
            "chatbot.views.generate_chat_response",
            return_value={"reply": "Try outside.", "mission": {}},
        ):
            response = self.client.post(
                "/api/chat/",
                {"message": "I have 20 minutes"},
                format="json",
            )
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.data["error"]["code"], "request_failed")

    def test_unexpected_chat_exception_returns_generic_json_without_traceback(self):
        client = APIClient(raise_request_exception=False)
        client.force_authenticate(
            user=SupabaseUser(id="verified-user-id", email="outside@example.com")
        )
        with self.assertLogs("config.api_errors", level="ERROR") as captured, patch(
            "chatbot.views.generate_chat_response",
            side_effect=RuntimeError("private internal marker"),
        ):
            response = client.post(
                "/api/chat/",
                {"message": "I have 20 minutes"},
                format="json",
            )
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response["Content-Type"], "application/json")
        self.assertEqual(response.data["error"]["code"], "request_failed")
        self.assertNotIn("private internal marker", response.content.decode())
        self.assertNotIn("Traceback", response.content.decode())
        self.assertNotIn("private internal marker", " ".join(captured.output))
        self.assertNotIn("Traceback", " ".join(captured.output))

    @override_settings(AI_PROVIDER="ollama", AI_MODEL="test-model")
    def test_unexpected_model_failure_does_not_log_message_or_exception(self):
        with self.assertLogs("chatbot", level="WARNING") as captured, patch(
            "chatbot.ai._post_json",
            side_effect=RuntimeError("private model marker"),
        ):
            response = self.client.post(
                "/api/chat/",
                {"message": "private user message marker"},
                format="json",
            )

        self.assertEqual(response.status_code, 200)
        logged = " ".join(captured.output)
        self.assertNotIn("private model marker", logged)
        self.assertNotIn("private user message marker", logged)
        self.assertNotIn("Traceback", logged)

    def test_chat_rejects_malformed_json_and_non_object_body(self):
        malformed = self.client.post(
            "/api/chat/",
            data=b'{"message":',
            content_type="application/json",
        )
        non_object = self.client.post(
            "/api/chat/",
            data='["not", "an object"]',
            content_type="application/json",
        )
        for response in (malformed, non_object):
            with self.subTest(status=response.status_code):
                self.assertEqual(response.status_code, 400)
                self.assertEqual(response.data["error"]["code"], "validation_error")

    def test_chat_method_not_allowed_uses_standard_error_envelope(self):
        response = self.client.get("/api/chat/")
        self.assertEqual(response.status_code, 405)
        self.assertEqual(response.data["error"]["code"], "request_failed")

    def test_chat_does_not_store_or_return_server_side_history(self):
        first_response = self.client.post(
            "/api/chat/",
            {"message": "I have 20 minutes and want to walk"},
            format="json",
        )
        second_response = self.client.post(
            "/api/chat/",
            {"message": "I have 20 minutes and want to walk"},
            format="json",
        )
        self.assertEqual(first_response.status_code, 200)
        self.assertEqual(second_response.status_code, 200)
        self.assertNotIn("history", first_response.data)
        self.assertNotIn("history", second_response.data)
        self.assertEqual(first_response.data["mission"], second_response.data["mission"])


@override_settings(ALLOWED_HOSTS=["testserver"])
class AiChatApiTests(SimpleTestCase):
    """POST /api/chat/ with the open-weight AI provider enabled (mocked)."""

    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(
            user=SupabaseUser(id="verified-user-id", email="outside@example.com")
        )

    @override_settings(AI_PROVIDER="ollama", AI_MODEL="test-model")
    def test_ai_success_returns_expected_api_structure(self):
        with patch(
            "chatbot.ai._post_json",
            return_value=ai_response(json.dumps(VALID_AI_MISSION)),
        ):
            response = self.client.post(
                "/api/chat/",
                {"message": "I have 45 minutes and want to explore"},
                format="json",
            )
        self.assertEqual(response.status_code, 200)
        self.assertIn("reply", response.data)
        mission = response.data["mission"]
        self.assertEqual(mission["title"], "A riverside breath break")
        self.assertEqual(mission["duration"], "45 minutes")
        self.assertEqual(mission["duration_minutes"], 45)
        self.assertEqual(len(mission["instructions"]), 3)
        self.assertEqual(mission["description"], mission["activity"])
        self.assertIn("challenge", mission)
        self.assertIn("bring", mission)
        self.assertEqual(mission["setting"], "outdoors")
        self.assertEqual(mission["energy_level"], "moderate")
        self.assertEqual(mission["type"], "outdoor_mission")
        self.assertNotIn("history", response.data)

    @override_settings(AI_PROVIDER="ollama", AI_MODEL="test-model")
    def test_model_unavailable_falls_back_to_rule_based(self):
        with patch(
            "chatbot.ai._post_json",
            side_effect=urllib.error.URLError("connection refused"),
        ):
            response = self.client.post(
                "/api/chat/",
                {"message": "I have 45 minutes and want to explore"},
                format="json",
            )
        self.assertEqual(response.status_code, 200)
        mission = response.data["mission"]
        self.assertEqual(mission["title"], "The tiny-things expedition")
        self.assertEqual(mission["duration"], "45 minutes")
        self.assertEqual(
            response.data["reply"],
            "I picked a curious little mission to help you notice your surroundings.",
        )

    @override_settings(AI_PROVIDER="ollama", AI_MODEL="test-model")
    def test_model_timeout_falls_back_at_the_chat_api(self):
        with patch("chatbot.ai._post_json", side_effect=TimeoutError):
            response = self.client.post(
                "/api/chat/",
                {"message": "I have 20 minutes and want to walk"},
                format="json",
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["mission"]["title"], "The unhurried wander")

    @override_settings(AI_PROVIDER="ollama", AI_MODEL="test-model")
    def test_malformed_model_output_falls_back_to_rule_based(self):
        with patch(
            "chatbot.ai._post_json",
            return_value=ai_response("Sorry, I cannot help with that."),
        ):
            response = self.client.post(
                "/api/chat/",
                {"message": "I have 20 minutes and want to walk"},
                format="json",
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["mission"]["title"], "The unhurried wander")

    @override_settings(AI_PROVIDER="ollama", AI_MODEL="test-model")
    def test_invalid_model_category_falls_back_without_exposing_model_error(self):
        invalid = dict(VALID_AI_MISSION, category="extreme_sports")
        with patch(
            "chatbot.ai._post_json",
            return_value=ai_response(json.dumps(invalid)),
        ):
            response = self.client.post(
                "/api/chat/",
                {"message": "I have 20 minutes and want to walk"},
                format="json",
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["mission"]["category"], "walking_exploring")
        self.assertNotIn("error", response.data)


@override_settings(AI_PROVIDER="ollama", AI_MODEL="test-model")
class AiConfigurationTests(SimpleTestCase):
    def test_ai_configuration_reads_settings(self):
        with override_settings(
            AI_PROVIDER="ollama",
            AI_MODEL="qwen2.5:3b",
            AI_BASE_URL="http://127.0.0.1:11434/",
            AI_TIMEOUT_SECONDS=7.5,
        ):
            config = ai.get_ai_config()
            provider = ai.get_provider()
        self.assertEqual(config["provider"], "ollama")
        self.assertEqual(config["model"], "qwen2.5:3b")
        self.assertEqual(config["base_url"], "http://127.0.0.1:11434")
        self.assertEqual(config["timeout"], 7.5)
        self.assertIsInstance(provider, ai.OllamaProvider)
        self.assertEqual(provider.model, "qwen2.5:3b")
        self.assertTrue(ai.ai_enabled())

    def test_rule_based_provider_disables_ai(self):
        with override_settings(AI_PROVIDER="rule_based"):
            self.assertIsNone(ai.get_provider())
            self.assertFalse(ai.ai_enabled())

    def test_unknown_provider_is_disabled_safely(self):
        with override_settings(AI_PROVIDER="some-other-service"):
            self.assertIsNone(ai.get_provider())
            self.assertFalse(ai.ai_enabled())

    def test_disabled_provider_rejects_ai_generation(self):
        with override_settings(AI_PROVIDER="rule_based"):
            with self.assertRaises(ai.AIError):
                ai.generate_ai_mission("I have 20 minutes", {})


class AiModelServiceTests(SimpleTestCase):
    @override_settings(AI_PROVIDER="ollama", AI_MODEL="test-model")
    def test_successful_model_response_returns_valid_mission(self):
        context = {"duration_minutes": 45, "mood": "curious"}
        with patch(
            "chatbot.ai._post_json",
            return_value=ai_response(json.dumps(VALID_AI_MISSION)),
        ) as post_json:
            mission = ai.generate_ai_mission("I have 45 minutes to explore", context)
        self.assertTrue(OutdoorMissionSerializer(data=mission).is_valid())
        self.assertEqual(mission["title"], "A riverside breath break")
        self.assertEqual(mission["duration"], "45 minutes")
        self.assertEqual(mission["description"], mission["activity"])
        payload = post_json.call_args.args[1]
        self.assertEqual(payload["model"], "test-model")
        self.assertFalse(payload["stream"])
        self.assertEqual(payload["format"], "json")

    @override_settings(AI_PROVIDER="ollama", AI_MODEL="test-model")
    def test_model_response_wrapped_in_markdown_is_parsed(self):
        content = "```json\n" + json.dumps(VALID_AI_MISSION) + "\n```"
        with patch("chatbot.ai._post_json", return_value=ai_response(content)):
            mission = ai.generate_ai_mission("I have 45 minutes", None)
        self.assertEqual(mission["title"], "A riverside breath break")

    @override_settings(AI_PROVIDER="ollama", AI_MODEL="test-model")
    def test_malformed_model_response_raises_ai_error(self):
        with patch(
            "chatbot.ai._post_json",
            return_value=ai_response("Sorry, I cannot help with that."),
        ):
            with self.assertRaises(ai.AIError):
                ai.generate_ai_mission("I have 45 minutes", None)

    @override_settings(AI_PROVIDER="ollama", AI_MODEL="test-model")
    def test_invalid_mission_fields_raise_ai_error(self):
        invalid_mission = dict(VALID_AI_MISSION, setting="beach")
        with patch(
            "chatbot.ai._post_json",
            return_value=ai_response(json.dumps(invalid_mission)),
        ):
            with self.assertRaises(ai.AIError):
                ai.generate_ai_mission("I have 45 minutes", None)

        missing_instructions = dict(VALID_AI_MISSION)
        missing_instructions["instructions"] = ["Only one step."]
        with patch(
            "chatbot.ai._post_json",
            return_value=ai_response(json.dumps(missing_instructions)),
        ):
            with self.assertRaises(ai.AIError):
                ai.generate_ai_mission("I have 45 minutes", None)

        invalid_difficulty = dict(VALID_AI_MISSION, difficulty="Extreme")
        with patch(
            "chatbot.ai._post_json",
            return_value=ai_response(json.dumps(invalid_difficulty)),
        ):
            with self.assertRaises(ai.AIError):
                ai.generate_ai_mission("I have 45 minutes", None)

        invalid_energy = dict(VALID_AI_MISSION, energy_level="maximum")
        with patch(
            "chatbot.ai._post_json",
            return_value=ai_response(json.dumps(invalid_energy)),
        ):
            with self.assertRaises(ai.AIError):
                ai.generate_ai_mission("I have 45 minutes", {"energy_level": "low"})

    @override_settings(AI_PROVIDER="ollama", AI_MODEL="test-model")
    def test_ai_mission_defaults_optional_fields_and_stays_within_available_time(self):
        context = {
            "available_minutes": 15,
            "duration_minutes": 15,
            "mood": "balanced",
            "energy_level": "moderate",
            "activity_preference": "unspecified",
            "setting_preference": "unspecified",
            "constraints": [],
            "difficulty_preference": "unspecified",
        }
        raw = dict(VALID_AI_MISSION)
        with patch(
            "chatbot.ai._post_json",
            return_value=ai_response(json.dumps(raw)),
        ):
            mission = ai.generate_ai_mission("I have 15 minutes", context)
        self.assertEqual(mission["duration_minutes"], 15)
        self.assertEqual(mission["category"], "walking_exploring")
        self.assertEqual(mission["difficulty"], "Easy")
        self.assertTrue(mission["safety_considerations"])

    @override_settings(AI_PROVIDER="ollama", AI_MODEL="test-model")
    def test_ai_mission_defaults_missing_optional_setting(self):
        raw = dict(VALID_AI_MISSION)
        raw.pop("setting")
        context = {
            "duration_minutes": 15,
            "setting_preference": "indoor",
            "energy_level": "low",
            "activity_preference": "unspecified",
            "constraints": [],
            "difficulty_preference": "unspecified",
        }
        with patch(
            "chatbot.ai._post_json",
            return_value=ai_response(json.dumps(raw)),
        ):
            mission = ai.generate_ai_mission("I would like to be outside", context)
        self.assertEqual(mission["setting"], "sheltered_outdoors")

    @override_settings(AI_PROVIDER="ollama", AI_MODEL="test-model")
    def test_ai_mission_does_not_reject_benign_no_equipment_text(self):
        raw = dict(VALID_AI_MISSION, bring="No equipment is needed.")
        context = {
            "available_minutes": 15,
            "duration_minutes": 15,
            "mood": "balanced",
            "energy_level": "low",
            "activity_preference": "unspecified",
            "setting_preference": "unspecified",
            "constraints": ["no_equipment"],
            "difficulty_preference": "unspecified",
        }
        with patch(
            "chatbot.ai._post_json",
            return_value=ai_response(json.dumps(raw)),
        ):
            mission = ai.generate_ai_mission("No equipment, please.", context)
        self.assertEqual(mission["duration_minutes"], 15)
        self.assertEqual(mission["category"], "relaxation_mindfulness")

    @override_settings(AI_PROVIDER="ollama", AI_MODEL="test-model")
    def test_ai_invalid_constraints_are_rejected_for_rule_fallback(self):
        unsafe = dict(
            VALID_AI_MISSION,
            activity="Climb a steep trail and explore off trail.",
            instructions=[
                "Choose a steep route with stairs.",
                "Climb to the top.",
                "Return along the trail.",
            ],
        )
        context = {
            "duration_minutes": 20,
            "energy_level": "low",
            "activity_preference": "unspecified",
            "setting_preference": "unspecified",
            "constraints": ["accessible_flat_route"],
            "difficulty_preference": "unspecified",
        }
        with patch(
            "chatbot.ai._post_json",
            return_value=ai_response(json.dumps(unsafe)),
        ):
            with self.assertRaises(ai.AIError):
                ai.generate_ai_mission("Avoid stairs; I need a flat route.", context)

    @override_settings(AI_PROVIDER="ollama", AI_MODEL="test-model")
    def test_ai_dangerous_activity_is_rejected(self):
        unsafe = dict(VALID_AI_MISSION, activity="Climb a steep wall to reach the view.")
        with patch(
            "chatbot.ai._post_json",
            return_value=ai_response(json.dumps(unsafe)),
        ):
            with self.assertRaises(ai.AIError):
                ai.generate_ai_mission("I want to explore outside.", {})

    @override_settings(AI_PROVIDER="ollama", AI_MODEL="test-model")
    def test_model_unavailable_raises_ai_error(self):
        with patch(
            "chatbot.ai._post_json",
            side_effect=urllib.error.URLError("connection refused"),
        ):
            with self.assertRaises(ai.AIError):
                ai.generate_ai_mission("I have 45 minutes", None)

    @override_settings(AI_PROVIDER="ollama", AI_MODEL="test-model")
    def test_model_timeout_raises_ai_error(self):
        with patch("chatbot.ai._post_json", side_effect=TimeoutError):
            with self.assertRaises(ai.AIError):
                ai.generate_ai_mission("I have 45 minutes", None)

    @override_settings(AI_PROVIDER="ollama", AI_MODEL="test-model")
    def test_rule_based_fallback_matches_direct_rule_based_result(self):
        message = "I have 45 minutes and want to explore"
        with patch(
            "chatbot.ai._post_json",
            side_effect=urllib.error.URLError("connection refused"),
        ):
            ai_response_dict = generate_chat_response(message)
        self.assertEqual(ai_response_dict["mission"], create_outdoor_mission(message))
        self.assertIn("reply", ai_response_dict)


class ChatbotServiceTests(SimpleTestCase):
    def test_service_rejects_empty_message(self):
        with self.assertRaises(ValueError):
            generate_chat_response(" ")

    def test_system_prompt_is_ready_for_future_model_integration(self):
        prompt = get_system_prompt()
        self.assertIn("outdoor mission", prompt)
        self.assertIn("structured mission", prompt)


class MissionApiTests(SimpleTestCase):
    def test_missions_are_available_without_authentication(self):
        response = APIClient().get("/api/missions/")
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(response.data["missions"]), 1)
