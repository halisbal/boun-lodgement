from rest_framework.permissions import BasePermission

from constants import UserRoles


class IsAuthenticatedAdmin(BasePermission):
    """
    Allows access only to authenticated users.
    """

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role in [UserRoles.ADMIN]
        )
