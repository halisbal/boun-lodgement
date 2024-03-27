from rest_framework import serializers

from .constants import UserRoles
from .models import User


class UserSerializer(serializers.ModelSerializer):
    role_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "role",
            "role_name",
            "is_active",
            "date_joined",
        ]

    def get_role_name(self, obj):
        return UserRoles(obj.role).label if obj.role in UserRoles.values else "Unknown"
