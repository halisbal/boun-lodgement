from rest_framework import serializers

from constants import LodgementType, PersonalType, LodgementSize
from .models import Lodgement, Queue


class QueueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Queue
        fields = ["lodgement_type", "personel_type", "lodgement_size"]

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
