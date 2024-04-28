from rest_framework import serializers

from authentication.serializers import UserSerializer
from constants import PersonalType
from core.constants import LodgementType, LodgementSize
from .models import Lodgement, Application, Queue, Form, FormItem


class QueueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Queue
        fields = ["id", "lodgement_type", "personel_type", "lodgement_size"]

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
            "required_documents",
            "queue",
            "tags",
        ]

    def get_tags(self, obj):
        return [
            LodgementType.choices[obj.queue.lodgement_type - 1][1],
            PersonalType.choices[obj.queue.personel_type - 1][1],
            LodgementSize.choices[obj.queue.lodgement_size - 1][1],
        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["required_documents"] = [
            doc.name for doc in instance.required_documents.all()
        ]
        return representation


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
        ]

    def get_status(self, obj):
        return obj.get_status_display()

    def get_scoring_form(self, obj):
        form = obj.scoring_form
        return FormSerializer(form).data if form else None

    def get_total_points(self, obj):
        return obj.scoring_form.total_points
