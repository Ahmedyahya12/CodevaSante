from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    PatientRegisterView,
    CustomLoginView,
    CurrentUserView,
    FirstLoginSetPasswordView,
    ChangePasswordView,
    ActivationSetPasswordView,
)

urlpatterns = [
    path("register/patient/", PatientRegisterView.as_view(), name="register-patient"),
    path("login/", CustomLoginView.as_view(), name="login"),
    path("refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("me/", CurrentUserView.as_view(), name="current-user"),
    path(
        "set-password/<uidb64>/<token>/",
        ActivationSetPasswordView.as_view(),
        name="activation-set-password",
    ),
    path(
        "first-login/set-password/",
        FirstLoginSetPasswordView.as_view(),
        name="first-login-set-password",
    ),
    path("change-password/", ChangePasswordView.as_view(), name="change-password"),
]
