from datetime import datetime
from functools import cached_property

from django.db import models
from dateutil.relativedelta import relativedelta
from django.db.models import Q, Case, When, BooleanField, Value, OuterRef, Subquery
from django.utils import timezone
import bisect
import numpy as np

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
    system_message = models.TextField(null=True, blank=True)

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

        today = timezone.now()
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

    def assign(self, application, lodgement):
        today = timezone.now().date()
        thirty_days_later = today + timezone.timedelta(days=30)
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

    def assignment_pipeline(self):
        if self.lodgement_type == LodgementType.SERVICE_ALLOCATION:
            # Service allocation will be handled manually by manager
            pass
        elif self.lodgement_type == LodgementType.DUTY_ALLOCATION:
            self.make_assignments_default()
        elif self.lodgement_type == LodgementType.SEQUENTIAL_ALLOCATION:
            if self.personel_type == PersonalType.ACADEMIC:
                self.make_assignments_academic()
            elif self.personel_type == PersonalType.ADMINISTRATIVE:
                self.make_assignments_default()

    def make_assignments_default(self):
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
            self.assign(application, lodgement)

    def make_assignments_academic(self):
        today = timezone.now().date()
        thirty_days_later = today + timezone.timedelta(days=30)
        threshold_date = datetime.now() - relativedelta(years=3)
        all_lodgements = list(self.lodgements.all())

        active_assignment_subquery = Assignment.objects.filter(
            lodgement=OuterRef("pk"),
            status__in=[AssignmentStatus.ACTIVE, AssignmentStatus.LOCKED],
        ).values("application__user__start_of_employment")[:1]

        # Annotate lodgements with is_new field
        assigned_lodgements = self.lodgements.annotate(
            start_of_employment=Subquery(active_assignment_subquery),
            is_new=Case(
                When(start_of_employment__gte=threshold_date, then=Value(True)),
                default=Value(False),
                output_field=BooleanField(),
            ),
        ).filter(busy_until__gte=thirty_days_later)

        new_academic_lodgements = [
            lodgement for lodgement in assigned_lodgements if lodgement.is_new
        ]
        print("New academic lodgements", new_academic_lodgements)
        old_academic_lodgements = [
            lodgement for lodgement in assigned_lodgements if not lodgement.is_new
        ]
        print("Old academic lodgements", old_academic_lodgements)

        assignable_lodgements = list(
            self.lodgements.filter(
                Q(busy_until__isnull=True) | Q(busy_until__lte=thirty_days_later)
            ).order_by("busy_until")
        )
        print("Assignable lodgements", assignable_lodgements)

        new_academic_applications = list(
            self.applications.filter(
                Q(
                    user__start_of_employment__gte=datetime.now()
                    - relativedelta(years=3)
                )
                & Q(status=ApplicationStatus.APPROVED)
            )
        )
        new_academic_applications.sort(
            key=lambda x: x.scoring_form.total_points, reverse=True
        )
        print("New academic applications", new_academic_applications)

        old_academic_applications = list(
            self.applications.filter(
                Q(user__start_of_employment__lt=datetime.now() - relativedelta(years=3))
                & Q(status=ApplicationStatus.APPROVED)
            )
        )
        old_academic_applications.sort(
            key=lambda x: x.scoring_form.total_points, reverse=True
        )
        print("Old academic applications", old_academic_applications)

        desired_vector = np.array(
            [0.8 * len(all_lodgements), 0.2 * len(all_lodgements)]
        )
        while assignable_lodgements and (
            new_academic_applications or old_academic_applications
        ):
            lodgement = assignable_lodgements.pop(0)

            new_academic_assignment_vector = np.array(
                [len(new_academic_lodgements) + 1, len(old_academic_lodgements)]
            )

            old_academic_assignment_vector = np.array(
                [len(new_academic_lodgements), len(old_academic_lodgements) + 1]
            )

            print(
                "Vector difference to desired vector if new academic is selected",
                np.linalg.norm(new_academic_assignment_vector - desired_vector),
            )
            print(
                "Vector difference to desired vector if old academic is selected",
                np.linalg.norm(old_academic_assignment_vector - desired_vector),
            )

            if np.linalg.norm(
                new_academic_assignment_vector - desired_vector
            ) < np.linalg.norm(old_academic_assignment_vector - desired_vector):
                if new_academic_applications:
                    print("New academic is selected")
                    application = new_academic_applications.pop(0)
                    self.assign(application, lodgement)
                else:
                    print(
                        "Old academic is selected since there are no new academic applications"
                    )
                    application = old_academic_applications.pop(0)
                    self.assign(application, lodgement)
            else:
                if old_academic_applications:
                    print("Old academic is selected")
                    application = old_academic_applications.pop(0)
                    self.assign(application, lodgement)
                else:
                    print(
                        "New academic is selected since there are no old academic applications"
                    )
                    application = new_academic_applications.pop(0)
                    self.assign(application, lodgement)

            active_assignment_subquery = Assignment.objects.filter(
                lodgement=OuterRef("pk"),
                status__in=[AssignmentStatus.ACTIVE, AssignmentStatus.LOCKED],
            ).values("application__user__start_of_employment")[:1]

            # Annotate lodgements with is_new field
            assigned_lodgements = self.lodgements.annotate(
                start_of_employment=Subquery(active_assignment_subquery),
                is_new=Case(
                    When(start_of_employment__gte=threshold_date, then=Value(True)),
                    default=Value(False),
                    output_field=BooleanField(),
                ),
            ).filter(busy_until__gte=thirty_days_later)

            new_academic_lodgements = [
                lodgement for lodgement in assigned_lodgements if lodgement.is_new
            ]
            print("New academic lodgements", new_academic_lodgements)
            old_academic_lodgements = [
                lodgement for lodgement in assigned_lodgements if not lodgement.is_new
            ]
            print("Old academic lodgements", old_academic_lodgements)

            assignable_lodgements = list(
                self.lodgements.filter(
                    Q(busy_until__isnull=True) | Q(busy_until__lte=thirty_days_later)
                ).order_by("busy_until")
            )
            print("Assignable lodgements", assignable_lodgements)

            new_academic_applications = list(
                self.applications.filter(
                    Q(
                        user__start_of_employment__gte=datetime.now()
                        - relativedelta(years=3)
                    )
                    & Q(status=ApplicationStatus.APPROVED)
                )
            )
            new_academic_applications.sort(
                key=lambda x: x.scoring_form.total_points, reverse=True
            )
            print("New academic applications", new_academic_applications)

            old_academic_applications = list(
                self.applications.filter(
                    Q(
                        user__start_of_employment__lt=datetime.now()
                        - relativedelta(years=3)
                    )
                    & Q(status=ApplicationStatus.APPROVED)
                )
            )
            old_academic_applications.sort(
                key=lambda x: x.scoring_form.total_points, reverse=True
            )
            print("Old academic applications", old_academic_applications)


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


class Announcement(BaseModel):
    title = models.CharField(max_length=200)
    content = models.TextField()
    is_visible = models.BooleanField(default=True)

    def __str__(self):
        return self.title
