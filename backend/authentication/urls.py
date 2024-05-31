from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import AuthView, MeView, UserViewSet

router = DefaultRouter()
router.register(r"user", UserViewSet)

app_name = "authentication"


urlpatterns = [
    path("login/", AuthView.as_view(), name="auth"),
    path("me/", MeView.as_view(), name="me"),
    path("", include(router.urls)),
]
