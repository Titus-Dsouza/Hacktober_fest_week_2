import json
from urllib.error import HTTPError, URLError
from unittest.mock import Mock, patch

from django.test import SimpleTestCase, override_settings
from rest_framework.test import APIClient
from rest_framework.exceptions import AuthenticationFailed

from .authentication import SupabaseUser, get_supabase_user


@override_settings(ALLOWED_HOSTS=["testserver"])
class SupabaseAuthenticationTests(SimpleTestCase):
    def setUp(self):
        self.client = APIClient()

    def test_verify_rejects_missing_access_token(self):
        response = self.client.get("/api/auth/verify/")
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data["error"]["code"], "authentication_required")

    @patch("users.authentication.get_supabase_user")
    def test_verify_accepts_valid_supabase_token(self, verify_user):
        verify_user.return_value = SupabaseUser(
            id="4b045250-7711-42db-8bcf-994622509fac",
            email="outside@example.com",
        )
        response = self.client.get(
            "/api/auth/verify/",
            HTTP_AUTHORIZATION="Bearer test-access-token",
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["authenticated"])
        self.assertEqual(response.data["user"]["email"], "outside@example.com")
        verify_user.assert_called_once_with("test-access-token")

    @patch("users.authentication.get_supabase_user")
    def test_profile_returns_verified_supabase_identity(self, verify_user):
        verify_user.return_value = SupabaseUser(
            id="4b045250-7711-42db-8bcf-994622509fac",
            email="outside@example.com",
        )
        response = self.client.get(
            "/api/auth/user/",
            HTTP_AUTHORIZATION="Bearer test-access-token",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["id"], "4b045250-7711-42db-8bcf-994622509fac")

    def test_malformed_bearer_header_is_rejected(self):
        response = self.client.get(
            "/api/auth/verify/",
            HTTP_AUTHORIZATION="Bearer token extra",
        )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data["error"]["code"], "authentication_required")

    @patch("users.authentication.get_supabase_user")
    def test_invalid_supabase_token_is_rejected(self, verify_user):
        verify_user.side_effect = AuthenticationFailed("Invalid token.")
        response = self.client.get(
            "/api/auth/verify/",
            HTTP_AUTHORIZATION="Bearer invalid-token",
        )
        self.assertEqual(response.status_code, 401)

    @patch("users.authentication.urlopen")
    def test_expired_supabase_token_is_rejected(self, open_url):
        open_url.side_effect = HTTPError(
            "https://touchgrass.supabase.co/auth/v1/user",
            401,
            "Unauthorized",
            {},
            None,
        )
        with patch.dict(
            "os.environ",
            {
                "SUPABASE_URL": "https://touchgrass.supabase.co",
                "SUPABASE_ANON_KEY": "test-publishable-key",
            },
        ):
            response = self.client.get(
                "/api/auth/verify/",
                HTTP_AUTHORIZATION="******",
            )
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data["error"]["code"], "authentication_required")

    @patch.dict(
        "os.environ",
        {
            "SUPABASE_URL": "https://touchgrass.supabase.co/",
            "SUPABASE_ANON_KEY": "test-publishable-key",
        },
    )
    @patch("users.authentication.urlopen")
    def test_user_verification_calls_supabase_auth(self, open_url):
        response = Mock()
        response.__enter__ = Mock(
            return_value=Mock(
                read=Mock(
                    return_value=json.dumps(
                        {"id": "verified-user", "email": "outside@example.com"}
                    ).encode()
                )
            )
        )
        response.__exit__ = Mock(return_value=False)
        open_url.return_value = response

        user = get_supabase_user("test-access-token")

        self.assertEqual(user, SupabaseUser("verified-user", "outside@example.com"))
        request = open_url.call_args.args[0]
        self.assertEqual(request.full_url, "https://touchgrass.supabase.co/auth/v1/user")
        self.assertEqual(request.get_header("Authorization"), "Bearer test-access-token")
        self.assertEqual(open_url.call_args.kwargs["timeout"], 5)

    @patch.dict(
        "os.environ",
        {
            "SUPABASE_URL": "https://touchgrass.supabase.co",
            "SUPABASE_ANON_KEY": "test-publishable-key",
        },
    )
    @patch("users.authentication.urlopen")
    def test_malformed_supabase_user_profile_is_rejected(self, open_url):
        response = Mock()
        response.__enter__ = Mock(return_value=Mock(read=Mock(return_value=b"[]")))
        response.__exit__ = Mock(return_value=False)
        open_url.return_value = response
        with self.assertRaises(AuthenticationFailed):
            get_supabase_user("test-access-token")

    @patch.dict(
        "os.environ",
        {
            "SUPABASE_URL": "https://touchgrass.supabase.co",
            "SUPABASE_ANON_KEY": "test-publishable-key",
        },
    )
    @patch("users.authentication.urlopen")
    def test_invalid_email_in_supabase_profile_is_rejected(self, open_url):
        response = Mock()
        response.__enter__ = Mock(
            return_value=Mock(
                read=Mock(
                    return_value=json.dumps(
                        {"id": "verified-user", "email": "not-an-email"}
                    ).encode()
                )
            )
        )
        response.__exit__ = Mock(return_value=False)
        open_url.return_value = response
        with self.assertRaises(AuthenticationFailed):
            get_supabase_user("test-access-token")

    @patch.dict("os.environ", {}, clear=True)
    def test_unconfigured_supabase_returns_service_unavailable(self):
        response = self.client.get(
            "/api/auth/verify/",
            HTTP_AUTHORIZATION="Bearer test-access-token",
        )
        self.assertEqual(response.status_code, 503, response.data)
        self.assertEqual(response.data["error"]["code"], "service_unavailable")

    def test_api_preflight_allows_configured_frontend_origin(self):
        response = self.client.options(
            "/api/chat/",
            HTTP_ORIGIN="http://localhost:8080",
            HTTP_ACCESS_CONTROL_REQUEST_METHOD="POST",
            HTTP_ACCESS_CONTROL_REQUEST_HEADERS="authorization,content-type",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response["access-control-allow-origin"],
            "http://localhost:8080",
        )

    def test_api_preflight_does_not_allow_unconfigured_origin(self):
        response = self.client.options(
            "/api/chat/",
            HTTP_ORIGIN="https://untrusted.example",
            HTTP_ACCESS_CONTROL_REQUEST_METHOD="POST",
            HTTP_ACCESS_CONTROL_REQUEST_HEADERS="authorization,content-type",
        )
        self.assertNotIn("access-control-allow-origin", response)

    @patch.dict(
        "os.environ",
        {
            "SUPABASE_URL": "https://touchgrass.supabase.co",
            "SUPABASE_ANON_KEY": "test-publishable-key",
        },
    )
    @patch("users.authentication.urlopen")
    def test_supabase_verification_outage_returns_service_unavailable(self, open_url):
        open_url.side_effect = URLError("network unavailable")
        response = self.client.get(
            "/api/auth/verify/",
            HTTP_AUTHORIZATION="Bearer outage-test-token",
        )
        open_url.assert_called_once()
        self.assertEqual(response.status_code, 503, response.data)
        self.assertEqual(response.data["error"]["code"], "service_unavailable")
        self.assertNotIn("network unavailable", str(response.data))
