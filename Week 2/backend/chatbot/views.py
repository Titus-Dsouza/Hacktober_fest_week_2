import logging

from rest_framework.exceptions import APIException
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import ChatRequestSerializer, ChatResponseSerializer
from .services import generate_chat_response

logger = logging.getLogger(__name__)


class ChatView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request_serializer = ChatRequestSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)

        try:
            generated_response = generate_chat_response(
                request_serializer.validated_data["message"]
            )
        except ValueError as exc:
            raise APIException("The chatbot could not process this message.") from exc

        response_serializer = ChatResponseSerializer(data=generated_response)
        if not response_serializer.is_valid():
            logger.error(
                "The chatbot generated an invalid response: %s",
                response_serializer.errors,
            )
            raise APIException("The chatbot generated an invalid response.")

        return Response(response_serializer.validated_data)
