from django.db.models import IntegerChoices

ALLOWED_EMAILS = [
    "halis.bal@std.bogazici.edu.tr",
    "emre.sin@std.bogazici.edu.tr",
    "birkan.yilmaz@bogazici.edu.tr",
]


class UserRoles(IntegerChoices):
    USER = 1, "User"
    LODGEMENT_MANAGER = 2, "Lodgement Manager"
    RESERVATION_MANAGER = 3, "Reservation Manager"
    MANAGER = 4, "Manager"
    ADMIN = 5, "Admin"


class PersonalType(IntegerChoices):
    ACADEMIC = 1, "Akademik"
    ADMINISTRATIVE = 2, "İdari"
    ATTENDANT = 3, "Görevli"
