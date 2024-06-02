from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    QueueViewSet,
    ApplicationViewSet,
    ScoringFormViewSet,
    LodgementViewSet,
    AnnouncementListView,
    FaqComponentListView,
)

app_name = "core"

router = DefaultRouter()
router.register(r"application", ApplicationViewSet)
router.register(r"queue", QueueViewSet)
router.register(r"scoring_form", ScoringFormViewSet)
router.register(r"lodgement", LodgementViewSet)
router.register(r"announcement", AnnouncementListView, basename="announcement")
router.register(r"faq", FaqComponentListView, basename="faq")

urlpatterns = [
    path("", include(router.urls)),
]
