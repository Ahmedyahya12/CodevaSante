from django.urls import path
from .views import (
    AvailableDoctorsListView,
    AdminCreateDoctorView,
    DoctorAvailabilityView,
    DoctorDetailView,
    DoctorMyProfileView,
    DoctorSpecialtiesView,
    DoctorUpdateMyProfileView,
)

urlpatterns = [
    path("", AvailableDoctorsListView.as_view()),
    path("specialties/", DoctorSpecialtiesView.as_view()),
    path("<int:pk>/", DoctorDetailView.as_view()),
    path("<int:pk>/availability/", DoctorAvailabilityView.as_view()),
    path("create/", AdminCreateDoctorView.as_view()),
    path("me/", DoctorMyProfileView.as_view(), name="doctor-my-profile"),
    path("me/update/", DoctorUpdateMyProfileView.as_view()),
]
