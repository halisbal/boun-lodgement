from django.db import models

from backend.src.core.constants import UserRoles


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class User(BaseModel):
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    role = models.IntegerField(choices=UserRoles.choices, default=UserRoles.USER)

    def __str__(self):
        return self.name
