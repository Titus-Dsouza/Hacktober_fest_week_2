from django.urls import path

from .views import MissionListView

urlpatterns = [
    path("missions/", MissionListView.as_view(), name="missions"),
]
