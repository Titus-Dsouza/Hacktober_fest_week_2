from django.test import SimpleTestCase, override_settings
from rest_framework.test import APIClient


@override_settings(ALLOWED_HOSTS=["testserver"])
class MissionListApiTests(SimpleTestCase):
    def setUp(self):
        self.client = APIClient()

    def test_public_mission_list_returns_sample_missions(self):
        response = self.client.get("/api/missions/")

        self.assertEqual(response.status_code, 200)
        self.assertIn("missions", response.data)
        self.assertGreaterEqual(len(response.data["missions"]), 1)
        self.assertTrue(
            all(
                {"id", "title", "description", "duration_minutes", "category"}
                <= mission.keys()
                for mission in response.data["missions"]
            )
        )

    def test_public_mission_list_does_not_require_authentication(self):
        response = APIClient().get("/api/missions/")

        self.assertEqual(response.status_code, 200)

    def test_mission_list_rejects_unsupported_methods_consistently(self):
        response = self.client.post("/api/missions/", {}, format="json")

        self.assertEqual(response.status_code, 405)
        self.assertEqual(response.data["error"]["code"], "request_failed")
