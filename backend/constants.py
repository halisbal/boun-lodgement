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


class LodgementSize(IntegerChoices):
    ONE_PLUS_ONE = 1, "1+1"
    TWO_PLUS_ONE = 2, "2+1"


class LodgementType(IntegerChoices):
    SEQUENTIAL_ALLOCATION = 1, "Sıra Tahsisli"
    SERVICE_ALLOCATION = 2, "Hizmet Tahsisli"
    DUTY_ALLOCATION = 3, "Görev Tahsisli"


class ApplicationStatus(IntegerChoices):
    PENDING = 1, "PENDING"
    APPROVED = 2, "APPROVED"
    REJECTED = 3, "REJECTED"
    RE_UPLOAD = 4, "RE_UPLOAD"
