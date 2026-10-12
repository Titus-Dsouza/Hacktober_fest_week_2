from rest_framework import serializers

from .mission_rules import DIFFICULTY_LEVELS, MISSION_CATEGORIES


class ChatRequestSerializer(serializers.Serializer):
    message = serializers.CharField(
        min_length=1,
        max_length=400,
        trim_whitespace=True,
    )

    def validate(self, attrs):
        if "history" in self.initial_data:
            raise serializers.ValidationError(
                {"history": "Conversation history is not supported."}
            )
        return attrs


class OutdoorMissionSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=120)
    duration = serializers.CharField(max_length=24)
    duration_minutes = serializers.IntegerField(min_value=1, max_value=120)
    activity = serializers.CharField(max_length=500)
    instructions = serializers.ListField(
        child=serializers.CharField(max_length=200),
        min_length=3,
        max_length=3,
    )
    description = serializers.CharField(max_length=500)
    challenge = serializers.CharField(max_length=200)
    bring = serializers.CharField(max_length=200)
    setting = serializers.ChoiceField(
        choices=("outdoors", "sheltered_outdoors")
    )
    energy_level = serializers.ChoiceField(choices=("low", "moderate", "high"))
    category = serializers.ChoiceField(choices=MISSION_CATEGORIES)
    difficulty = serializers.ChoiceField(choices=DIFFICULTY_LEVELS)
    safety_considerations = serializers.CharField(max_length=300)
    type = serializers.ChoiceField(choices=("outdoor_mission",))


class ChatResponseSerializer(serializers.Serializer):
    reply = serializers.CharField()
    mission = OutdoorMissionSerializer()
