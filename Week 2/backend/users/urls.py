from django.urls import path

from .views import CurrentUserView, VerifyTokenView

urlpatterns = [
    path("verify/", VerifyTokenView.as_view(), name="auth-verify"),
    path("user/", CurrentUserView.as_view(), name="current-user"),
]
