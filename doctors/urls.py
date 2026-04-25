from django.urls import path
from .views import (
    AvailableDoctorsListView,
    AdminCreateDoctorView,
    DoctorMyProfileView,
    DoctorUpdateMyProfileView,
)

urlpatterns = [
    path("", AvailableDoctorsListView.as_view(), name="available-doctors"),
    path("create/", AdminCreateDoctorView.as_view(), name="admin-create-doctor"),
    path("me/", DoctorMyProfileView.as_view(), name="doctor-my-profile"),
    path("me/update/", DoctorUpdateMyProfileView.as_view(), name="doctor-update-profile"),
]