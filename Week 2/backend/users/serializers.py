from rest_framework import serializers


class UserProfileSerializer(serializers.Serializer):
    id = serializers.CharField()
    email = serializers.EmailField()
