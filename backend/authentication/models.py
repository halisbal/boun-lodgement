from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

from constants import UserRoles, PersonalType


class User(AbstractUser):
    email = models.EmailField(max_length=100)
    role = models.IntegerField(choices=UserRoles.choices, default=UserRoles.USER)
    type = models.IntegerField(
        choices=PersonalType.choices, default=PersonalType.ACADEMIC
    )
    start_of_employment = models.DateField(null=True, blank=True)

    groups = models.ManyToManyField(Group, related_name="custom_user_set", blank=True)
    user_permissions = models.ManyToManyField(
        Permission, related_name="custom_user_permission_set", blank=True
    )

    def __str__(self):
        return self.first_name
