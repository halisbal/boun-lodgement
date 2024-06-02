from rest_framework import serializers

from constants import UserRoles, PersonalType
from .models import User


class UserSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "role",
            "type",
            "is_active",
            "date_joined",
        ]

    def get_role(self, obj):
        return UserRoles(obj.role).label if obj.role in UserRoles.values else "Unknown"

    def get_type(self, obj):
        return (
            PersonalType(obj.type).label
            if obj.type in PersonalType.values
            else "Unknown"
        )


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "role", "type", "is_active"]
