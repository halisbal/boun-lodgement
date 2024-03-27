from django.db.models import IntegerChoices

ALLOWED_EMAILS = [
    "halis.bal@std.bogazici.edu.tr",
    "emre.sin@std.bogazici.edu.tr",
    "birkan.yilmaz@bogazici.edu.tr",
]


class UserRoles(IntegerChoices):
    USER = 1, "User"
    MANAGER = 2, "Manager"
    ADMIN = 3, "Admin"
