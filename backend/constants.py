from django.db.models import IntegerChoices

ALLOWED_EMAILS = [
    "halis.bal@std.bogazici.edu.tr",
    "emre.sin@std.bogazici.edu.tr",
    "birkan.yilmaz@bogazici.edu.tr",
    "akarun@bogazici.edu.tr",
    "ersoy@bogazici.edu.tr",
    "arzucan.ozgur@bogazici.edu.tr",
    "say@bogazici.edu.tr",
    "tuna.tugcu@gmail.com",
]


class UserRoles(IntegerChoices):
    USER = 1, "User"
    MANAGER = 2, "Manager"
    ADMIN = 3, "Admin"


class PersonalType(IntegerChoices):
    ACADEMIC = 1, "Akademik"
    ADMINISTRATIVE = 2, "İdari"
    ATTENDANT = 3, "Görevli"
