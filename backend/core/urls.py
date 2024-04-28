from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import LodgementListView, ApplyQueueView, ApplicationViewSet

app_name = "core"

router = DefaultRouter()
router.register(r"application", ApplicationViewSet)

urlpatterns = [
    path("lodgement/list/", LodgementListView.as_view(), name="lodgement_list"),
    path("apply_queue/", ApplyQueueView.as_view(), name="apply_queue"),
    path("", include(router.urls)),
]
