from django.db import models

from authentication.models import User
from constants import (
    LodgementSize,
    ApplicationStatus,
    PersonalType,
    LodgementType,
)


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Lodgement(BaseModel):
    size = models.IntegerField(choices=LodgementSize.choices)
    description = models.TextField()
    location = models.CharField(max_length=255)
    is_available = models.BooleanField(default=True)
    busy_until = models.DateTimeField(null=True)
    required_documents = models.ManyToManyField("Document", related_name="lodgements")
    queue = models.ForeignKey(
        "Queue", on_delete=models.CASCADE, related_name="lodgements"
    )


class Document(BaseModel):
    name = models.CharField(max_length=255)
    form = models.TextField(help_text="Base64 encoded PDF file")


class Application(BaseModel):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="applications"
    )
    status = models.IntegerField(choices=ApplicationStatus.choices)
    queue = models.ForeignKey(
        "Queue", on_delete=models.CASCADE, related_name="applications"
    )
    points = models.IntegerField()
    documents = models.ManyToManyField("Document", through="ApplicationDocument")


class ApplicationDocument(BaseModel):
    document = models.ForeignKey(
        "Document", on_delete=models.CASCADE, related_name="application_documents"
    )
    application = models.ForeignKey(
        "Application", on_delete=models.CASCADE, related_name="application_documents"
    )
    is_approved = models.BooleanField(default=False)


class Queue(BaseModel):
    lodgement_type = models.IntegerField(choices=LodgementType.choices)
    personel_type = models.IntegerField(choices=PersonalType.choices)


class Assignment(BaseModel):
    application = models.ForeignKey(
        "Application", on_delete=models.CASCADE, related_name="assignments"
    )
    lodgement = models.ForeignKey(
        "Lodgement", on_delete=models.CASCADE, related_name="assignments"
    )
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    status = models.IntegerField()
    is_deposit_paid = models.BooleanField(default=False)
