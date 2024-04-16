from django.contrib import admin
from .models import (
    Lodgement,
    Document,
    Application,
    ApplicationDocument,
    Queue,
    Assignment,
)


class LodgementAdmin(admin.ModelAdmin):
    list_display = ["description", "size", "location", "is_available", "busy_until"]
    list_filter = ["is_available", "size"]
    search_fields = ["description", "location"]


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
    list_display = ["lodgement_type", "personel_type"]
    list_filter = ["lodgement_type", "personel_type"]


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
