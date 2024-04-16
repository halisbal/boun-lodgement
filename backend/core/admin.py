from django.contrib import admin

from constants import LodgementType, PersonalType, LodgementSize
from .models import (
    Lodgement,
    Document,
    Application,
    ApplicationDocument,
    Queue,
    Assignment,
)


class LodgementAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "description",
        "size",
        "location",
        "is_available",
        "busy_until",
        "get_lodgement_type",
        "get_personel_type",
        "get_lodgement_size",
    ]
    list_filter = ["is_available", "size"]
    search_fields = ["description", "location"]

    def get_lodgement_type(self, obj):
        return LodgementType.choices[obj.queue.lodgement_type - 1][1]

    get_lodgement_type.short_description = "Lodgement Type"

    def get_personel_type(self, obj):
        return PersonalType.choices[obj.queue.personel_type - 1][1]

    get_personel_type.short_description = "Personel Type"

    def get_lodgement_size(self, obj):
        return LodgementSize.choices[obj.queue.lodgement_size - 1][1]

    get_lodgement_size.short_description = "Lodgement Size"


class DocumentAdmin(admin.ModelAdmin):
    list_display = ["name", "form"]
    search_fields = ["name"]


class ApplicationAdmin(admin.ModelAdmin):
    list_display = ["user", "status", "points"]
    list_filter = ["status"]
    search_fields = ["user__username", "user__email"]


class ApplicationDocumentAdmin(admin.ModelAdmin):
    list_display = ["document", "application", "is_approved"]
    list_filter = ["is_approved"]


class QueueAdmin(admin.ModelAdmin):
    list_display = ["lodgement_type", "personel_type", "lodgement_size"]
    list_filter = ["lodgement_type", "personel_type", "lodgement_size"]


class AssignmentAdmin(admin.ModelAdmin):
    list_display = [
        "application",
        "lodgement",
        "start_date",
        "end_date",
        "status",
        "is_deposit_paid",
    ]
    list_filter = ["status", "is_deposit_paid"]
    date_hierarchy = "start_date"


admin.site.register(Lodgement, LodgementAdmin)
admin.site.register(Document, DocumentAdmin)
admin.site.register(Application, ApplicationAdmin)
admin.site.register(ApplicationDocument, ApplicationDocumentAdmin)
admin.site.register(Queue, QueueAdmin)
admin.site.register(Assignment, AssignmentAdmin)
