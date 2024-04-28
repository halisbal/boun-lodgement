from rest_framework import serializers

from constants import UserRoles
from .models import User


class UserSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "role",
            "is_active",
            "date_joined",
        ]

    def get_role(self, obj):
        return UserRoles(obj.role).label if obj.role in UserRoles.values else "Unknown"
