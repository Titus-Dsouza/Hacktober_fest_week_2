import json
import logging
import os
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from rest_framework.authentication import BaseAuthentication, get_authorization_header
from rest_framework.exceptions import APIException, AuthenticationFailed

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class SupabaseUser:
    id: str
    email: str

    @property
    def pk(self):
        return self.id

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False


class SupabaseAuthUnavailable(APIException):
    status_code = 503
    default_detail = "Authentication service is temporarily unavailable."
    default_code = "authentication_service_unavailable"


def get_supabase_user(access_token):
    project_url = os.getenv("SUPABASE_URL", "").rstrip("/")
    anon_key = os.getenv("SUPABASE_ANON_KEY", "")
    if not project_url or not anon_key:
        logger.error("Supabase authentication is not configured on the server.")
        raise SupabaseAuthUnavailable(
            "Set SUPABASE_URL and SUPABASE_ANON_KEY in the server environment."
        )

    request = Request(
        f"{project_url}/auth/v1/user",
        headers={
            "apikey": anon_key,
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
        },
    )
    try:
        with urlopen(request, timeout=5) as response:
            payload = json.loads(response.read())
    except HTTPError as exc:
        if exc.code in (401, 403):
            raise AuthenticationFailed("The Supabase access token is invalid or expired.") from exc
        logger.warning("Supabase user verification failed with HTTP %s.", exc.code)
        raise SupabaseAuthUnavailable() from exc
    except (URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
        logger.warning("Could not reach the Supabase user verification endpoint.")
        raise SupabaseAuthUnavailable() from exc

    if not isinstance(payload, dict):
        raise AuthenticationFailed("Supabase returned an invalid user profile.")
    user_id = payload.get("id")
    email = payload.get("email")
    if not isinstance(user_id, str) or not user_id or not isinstance(email, str):
        raise AuthenticationFailed("Supabase returned an invalid user profile.")
    try:
        validate_email(email)
    except ValidationError as exc:
        raise AuthenticationFailed("Supabase returned an invalid user profile.") from exc
    return SupabaseUser(id=user_id, email=email)


class SupabaseTokenAuthentication(BaseAuthentication):
    keyword = b"bearer"

    def authenticate(self, request):
        parts = get_authorization_header(request).split()
        if not parts:
            return None
        if parts[0].lower() != self.keyword:
            return None
        if len(parts) != 2:
            raise AuthenticationFailed("Invalid Authorization header.")
        try:
            access_token = parts[1].decode("ascii")
        except UnicodeDecodeError as exc:
            raise AuthenticationFailed("Invalid Authorization header.") from exc
        if not access_token:
            raise AuthenticationFailed("Invalid Authorization header.")
        return get_supabase_user(access_token), None

    def authenticate_header(self, request):
        return "Bearer"
