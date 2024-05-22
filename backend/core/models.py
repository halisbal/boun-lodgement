from datetime import datetime
from functools import cached_property

from django.db import models
from dateutil.relativedelta import relativedelta
from django.db.models import Q
from django.utils import timezone
import bisect

from authentication.models import User
from constants import (
    PersonalType,
)
from core.constants import (
    FormType,
    FormItemTypes,
    LodgementSize,
    ApplicationStatus,
    LodgementType,
    AssignmentStatus,
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
    name = models.TextField()
    description = models.TextField(null=True, blank=True)
    pdf_file = models.FileField(upload_to="documents/", null=True, blank=True)


class Application(BaseModel):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="applications"
    )
    status = models.IntegerField(choices=ApplicationStatus.choices)
    queue = models.ForeignKey(
        "Queue", on_delete=models.CASCADE, related_name="applications"
    )

    @property
    def scoring_form(self):
        return self.forms.filter(type=FormType.SCORING).first()


class Form(BaseModel):
    type = models.IntegerField(choices=FormType.choices)
    application = models.ForeignKey(
        "Application", on_delete=models.CASCADE, related_name="forms"
    )

    @cached_property
    def total_points(self):
        items = self.items.all()
        s = 0
        for item in items:
            if item.point:
                if item.field_type == FormItemTypes.INTEGER:
                    s += item.point * item.answer_value if item.answer_value else 0
                elif item.field_type == FormItemTypes.BOOLEAN:
                    s += item.point if item.answer_value else 0
        years_waited = relativedelta(
            datetime.now(), self.created_at.replace(tzinfo=None)
        ).years
        return s + years_waited


class FormItem(BaseModel):
    label = models.TextField()
    caption = models.TextField()
    field_type = models.IntegerField(choices=FormItemTypes.choices)
    form = models.ForeignKey("Form", on_delete=models.CASCADE, related_name="items")
    point = models.IntegerField(null=True, blank=True)
    answer = models.JSONField(null=True, blank=True)

    @property
    def answer_value(self):
        if self.answer is None or "value" not in self.answer:
            return None

        value = self.answer.get("value")

        if self.field_type == FormItemTypes.INTEGER:
            try:
                return int(value)
            except (TypeError, ValueError):
                return None
        elif self.field_type == FormItemTypes.BOOLEAN:
            return bool(value)
        elif self.field_type == FormItemTypes.TEXT:
            return str(value)

        return None


class ApplicationDocument(BaseModel):
    document = models.ForeignKey(
        "Document", on_delete=models.CASCADE, related_name="application_documents"
    )
    application = models.ForeignKey(
        "Application", on_delete=models.CASCADE, related_name="documents"
    )
    file = models.FileField(upload_to="application_documents/")
    description = models.TextField()
    is_approved = models.BooleanField(default=False)


class Queue(BaseModel):
    lodgement_type = models.IntegerField(choices=LodgementType.choices)
    personel_type = models.IntegerField(choices=PersonalType.choices)
    lodgement_size = models.IntegerField(choices=LodgementSize.choices, default=1)
    required_documents = models.ManyToManyField(
        "Document", related_name="queues", blank=True
    )

    def __str__(self):
        return f"{LodgementType.choices[self.lodgement_type - 1][1]} - {PersonalType.choices[self.personel_type - 1][1]} - {LodgementSize.choices[self.lodgement_size - 1][1]}"

    def get_priority_queue(self, new_application=None, new_application_points=None):
        applications = list(self.applications.filter(status=ApplicationStatus.APPROVED))
        # Sort applications in Python based on the scoring_form property
        applications.sort(key=lambda x: x.scoring_form.total_points, reverse=True)

        if new_application is not None and new_application_points is not None:
            points_list = [app.scoring_form.total_points for app in applications]
            # Find the position where the new application should be inserted
            position = bisect.bisect_right(
                [-points for points in points_list], -new_application_points
            )
            # Insert the new application at the correct position
            applications.insert(position, new_application)

        lodgements = self.lodgements.order_by("busy_until")
        available_lodgements = lodgements.filter(busy_until__isnull=True)
        busy_lodgements = lodgements.filter(busy_until__isnull=False)

        today = timezone.now().date()
        availability_queue = []

        # Assign immediate availability to applications if there are available lodgements
        for application in applications:
            if available_lodgements:
                lodgement = available_lodgements[0]
                availability_queue.append(
                    {
                        "application": application,
                        "total_points": application.scoring_form.total_points
                        if application.id != -1
                        else new_application_points,
                        "estimated_availability_date": today,
                        "lodgement": lodgement,
                    }
                )
                available_lodgements = available_lodgements[
                    1:
                ]  # Move to the next available lodgement
            else:
                # If no available lodgements, assign based on the earliest busy_until
                if busy_lodgements:
                    earliest_busy = busy_lodgements[0]
                    availability_queue.append(
                        {
                            "application": application,
                            "total_points": application.scoring_form.total_points
                            if application.id != -1
                            else new_application_points,
                            "estimated_availability_date": earliest_busy.busy_until,
                            "lodgement": earliest_busy,
                        }
                    )
                    busy_lodgements = busy_lodgements[
                        1:
                    ]  # Move to the next busy lodgement
                else:
                    availability_queue.append(
                        {
                            "application": application,
                            "total_points": application.scoring_form.total_points
                            if application.id != -1
                            else new_application_points,
                            "estimated_availability_date": None,
                            "lodgement": None,
                        }
                    )

        return availability_queue

    def make_assignments(self):
        applications = list(self.applications.filter(status=ApplicationStatus.APPROVED))
        applications.sort(key=lambda x: x.scoring_form.total_points, reverse=True)

        today = timezone.now().date()
        thirty_days_later = today + timezone.timedelta(days=30)
        lodgements = list(
            self.lodgements.filter(
                Q(busy_until__isnull=True) | Q(busy_until__lte=thirty_days_later)
            ).order_by("busy_until")
        )

        while applications and lodgements:
            application = applications.pop(0)
            lodgement = lodgements.pop(0)
            assignment = Assignment(
                application=application,
                lodgement=lodgement,
                start_date=thirty_days_later,
                end_date=thirty_days_later + timezone.timedelta(days=365 * 5),
                status=AssignmentStatus.LOCKED,
            )
            assignment.save()
            lodgement.busy_until = assignment.end_date
            lodgement.save()
            application.status = ApplicationStatus.ASSIGNED
            application.save()


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


class ScoringFormItem(models.Model):
    type = models.IntegerField(choices=FormType.choices)
    label = models.TextField()
    caption = models.TextField()
    field_type = models.IntegerField(choices=FormItemTypes.choices)
    point = models.IntegerField(null=True, blank=True)


class ScoringFormLog(models.Model):
    data = models.JSONField()
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="scoring_form_logs"
    )
