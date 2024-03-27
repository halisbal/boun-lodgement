from django.urls import path
from .views import AuthView, MeView


app_name = "authentication"
urlpatterns = [
    path("login/", AuthView.as_view(), name="auth"),
    path("me/", MeView.as_view(), name="me"),
]
