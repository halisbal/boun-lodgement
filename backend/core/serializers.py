from datetime import datetime

import pytz
from rest_framework import serializers

from authentication.serializers import UserSerializer
from constants import PersonalType
from core.constants import LodgementType, LodgementSize, ApplicationStatus, days_until
from .models import (
    Lodgement,
    Application,
    Queue,
    Form,
    FormItem,
    Document,
    ApplicationDocument,
    Announcement,
    FaqComponent,
)


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ["id", "name", "description", "pdf_file"]


class ApplicationDocumentSerializer(serializers.ModelSerializer):
    document = DocumentSerializer(read_only=True)

    class Meta:
        model = ApplicationDocument
        fields = ["file", "description", "is_approved", "document"]


class QueueSerializer(serializers.ModelSerializer):
    required_documents = DocumentSerializer(many=True)

    class Meta:
        model = Queue
        fields = [
            "id",
            "lodgement_type",
            "personel_type",
            "lodgement_size",
            "required_documents",
        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["lodgement_type"] = LodgementType.choices[
            instance.lodgement_type - 1
        ][1]
        representation["personel_type"] = PersonalType.choices[
            instance.personel_type - 1
        ][1]
        representation["lodgement_size"] = LodgementSize.choices[
            instance.lodgement_size - 1
        ][1]
        return representation


class QueueReadOnlySerializer(serializers.ModelSerializer):
    class Meta:
        model = Queue
        fields = [
            "id",
            "lodgement_type",
            "personel_type",
            "lodgement_size",
        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["lodgement_type"] = LodgementType.choices[
            instance.lodgement_type - 1
        ][1]
        representation["personel_type"] = PersonalType.choices[
            instance.personel_type - 1
        ][1]
        representation["lodgement_size"] = LodgementSize.choices[
            instance.lodgement_size - 1
        ][1]
        return representation


class LodgementSerializer(serializers.ModelSerializer):
    queue = QueueSerializer(read_only=True)
    queue_id = serializers.PrimaryKeyRelatedField(
        queryset=Queue.objects.all(), source="queue"
    )
    tags = serializers.SerializerMethodField()

    class Meta:
        model = Lodgement
        fields = [
            "id",
            "name",
            "size",
            "description",
            "image_path",
            "location",
            "is_available",
            "busy_until",
            "queue",
            "queue_id",
            "tags",
        ]

    def get_tags(self, obj):
        return [
            LodgementType.choices[obj.queue.lodgement_type - 1][1],
            PersonalType.choices[obj.queue.personel_type - 1][1],
            LodgementSize.choices[obj.queue.lodgement_size - 1][1],
        ]


class FormItemSerializer(serializers.ModelSerializer):
    field_type = serializers.SerializerMethodField()

    class Meta:
        model = FormItem
        fields = ["id", "label", "caption", "field_type", "point", "answer"]

    def get_field_type(self, obj):
        return obj.get_field_type_display()


class FormSerializer(serializers.ModelSerializer):
    type = serializers.SerializerMethodField()
    items = FormItemSerializer(many=True, read_only=True)

    class Meta:
        model = Form
        fields = ["id", "type", "items"]

    def get_type(self, obj):
        return obj.get_type_display()


class ApplicationSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()
    queue = QueueSerializer(read_only=True)
    user = UserSerializer(read_only=True)
    scoring_form = serializers.SerializerMethodField()
    total_points = serializers.SerializerMethodField()
    documents = ApplicationDocumentSerializer(many=True)
    created_at = serializers.SerializerMethodField()
    estimated_availability = serializers.SerializerMethodField()
    rank = serializers.SerializerMethodField()
    is_locked = serializers.SerializerMethodField()

    class Meta:
        model = Application
        fields = [
            "id",
            "user",
            "status",
            "queue",
            "scoring_form",
            "documents",
            "total_points",
            "created_at",
            "estimated_availability",
            "rank",
            "is_locked",
        ]

    def get_status(self, obj):
        return obj.get_status_display()

    def get_scoring_form(self, obj):
        form = obj.scoring_form
        return FormSerializer(form).data if form else None

    def get_total_points(self, obj):
        return obj.scoring_form.total_points

    def get_created_at(self, obj):
        return obj.created_at.astimezone(tz=pytz.timezone("Asia/Istanbul")).strftime(
            "%d %B %Y, %H:%M"
        )

    def get_estimated_availability(self, obj):
        if obj.queue.lodgements.count() == 0:
            approximate_availability = None
        else:
            if obj.status == ApplicationStatus.APPROVED:
                pq = obj.queue.get_priority_queue()
                approximate_availability = list(
                    filter(lambda x: x.get("application").id == obj.id, pq)
                )[0].get("estimated_availability_date")
            else:
                new_application = Application(user=obj.user, queue=obj.queue, id=-1)
                pq = obj.queue.get_priority_queue(
                    new_application=new_application,
                    new_application_points=obj.scoring_form.total_points,
                )
                approximate_availability = list(
                    filter(lambda x: x.get("application").id == -1, pq)
                )[0].get("estimated_availability_date")
        return days_until(approximate_availability)

    def get_rank(self, obj):
        applications = obj.queue.applications.filter(
            status__in=[ApplicationStatus.APPROVED],
        )
        current_rank = 1
        for application in applications:
            if application.user == obj.user:
                continue
            if application.scoring_form.total_points > obj.scoring_form.total_points:
                current_rank += 1
        return current_rank

    def get_is_locked(self, obj):
        return obj.status in [
            ApplicationStatus.APPROVED,
            ApplicationStatus.REJECTED,
            ApplicationStatus.CANCELLED,
            ApplicationStatus.PENDING,
            ApplicationStatus.ASSIGNED,
        ]


class ApplicationListSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()
    queue = QueueReadOnlySerializer(read_only=True)

    class Meta:
        model = Application
        fields = [
            "id",
            "status",
            "queue",
        ]

    def get_status(self, obj):
        return obj.get_status_display()


class ScoringFormItemSerializer(serializers.ModelSerializer):
    field_type = serializers.SerializerMethodField()

    class Meta:
        model = FormItem
        fields = ["id", "label", "caption", "field_type", "point"]

    def get_field_type(self, obj):
        return obj.get_field_type_display()


class AnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcement
        fields = ["id", "created_at", "title", "content"]


class FaqComponentSerializer(serializers.ModelSerializer):
    class Meta:
        model = FaqComponent
        fields = ["question", "answer", "order"]
