from django.urls import path
from .views import (
    PatientMyProfileView,
    ReceptionistPatientSearchView,
    ReceptionistCreatePatientView,
    DoctorMyPatientsView,
)

urlpatterns = [
    path("me/", PatientMyProfileView.as_view(), name="patient-my-profile"),
    path("search/", ReceptionistPatientSearchView.as_view(), name="patient-search"),
    path("create/", ReceptionistCreatePatientView.as_view(), name="patient-create"),
    path("my-doctor-patients/", DoctorMyPatientsView.as_view(), name="doctor-my-patients"),
]