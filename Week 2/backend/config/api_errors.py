import logging

from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = logging.getLogger(__name__)


def api_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is None:
        request = context.get("request")
        logger.error(
            "Unhandled API exception for %s %s (%s).",
            request.method if request else "unknown method",
            request.path if request else "unknown path",
            type(exc).__name__,
        )
        return Response(
            {
                "error": {
                    "code": "request_failed",
                    "message": "The request could not be completed.",
                    "details": None,
                }
            },
            status=500,
        )

    if response.status_code == 400:
        code = "validation_error"
        message = "Request validation failed."
        details = response.data
    elif response.status_code == 401:
        code = "authentication_required"
        message = "A valid Supabase access token is required."
        details = None
    elif response.status_code == 403:
        code = "permission_denied"
        message = "You do not have permission to perform this action."
        details = None
    elif response.status_code == 404:
        code = "not_found"
        message = "The requested resource was not found."
        details = None
    elif response.status_code == 503:
        code = "service_unavailable"
        message = "A required service is temporarily unavailable."
        details = None
    else:
        code = "request_failed"
        message = "The request could not be completed."
        details = response.data

    response.data = {"error": {"code": code, "message": message, "details": details}}
    return response
