from django.urls import path
from .views import *

urlpatterns = [
    path("create/", DoctorCreateMedicalRecordView.as_view()),
    path("doctor/", DoctorPatientRecordsView.as_view()),
    path("me/", PatientMyRecordsView.as_view()),
]