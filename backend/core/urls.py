from django.urls import path
from .views import LodgementListView


app_name = "core"
urlpatterns = [
    path("lodgement/list/", LodgementListView.as_view(), name="lodgement_list"),
]
