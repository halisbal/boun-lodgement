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
    name = models.CharField(max_length=255, null=True, blank=True)
    size = models.IntegerField(choices=LodgementSize.choices)
    description = models.TextField()
    image_path = models.CharField(max_length=255, null=True, blank=True)
    location = models.CharField(max_length=255)
    is_available = models.BooleanField(default=True)
    busy_until = models.DateTimeField(null=True, blank=True)
    required_documents = models.ManyToManyField(
        "Document", related_name="lodgements", blank=True
    )
    queue = models.ForeignKey(
        "Queue", on_delete=models.CASCADE, related_name="lodgements"
    )


class Document(BaseModel):
    name = models.CharField(max_length=255)
    pdf_path = models.CharField(max_length=255, null=True, blank=True)


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
    lodgement_size = models.IntegerField(choices=LodgementSize.choices, default=1)

    def __str__(self):
        return f"{LodgementType.choices[self.lodgement_type - 1][1]} - {PersonalType.choices[self.personel_type - 1][1]} - {LodgementSize.choices[self.lodgement_size - 1][1]}"


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
