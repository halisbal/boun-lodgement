from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import LodgementListView, QueueViewSet, ApplicationViewSet

app_name = "core"

router = DefaultRouter()
router.register(r"application", ApplicationViewSet)
router.register(r"queue", QueueViewSet)

urlpatterns = [
    path("lodgement/list/", LodgementListView.as_view(), name="lodgement_list"),
    path("", include(router.urls)),
]
