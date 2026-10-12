from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

MISSIONS = [
    {
        "id": "slow-stroll",
        "title": "The slow stroll",
        "description": "Take the scenic route. No destination needed.",
        "duration_minutes": 30,
        "category": "relax",
    },
    {
        "id": "listen-closely",
        "title": "Listen closely",
        "description": "Find a spot and notice three sounds around you.",
        "duration_minutes": 20,
        "category": "mindful",
    },
    {
        "id": "little-details",
        "title": "Little details",
        "description": "Look for tiny colors, textures, and new things.",
        "duration_minutes": 15,
        "category": "explore",
    },
]


class MissionListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"missions": MISSIONS})
