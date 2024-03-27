from django.db.models import IntegerChoices

ALLOWED_EMAILS = ["halis.bal@std.boun.edu.tr", "emre.sin@std.boun.edu.tr"]


class UserRoles(IntegerChoices):
    USER = 1, "User"
    MANAGER = 2, "Manager"
    ADMIN = 3, "Admin"
