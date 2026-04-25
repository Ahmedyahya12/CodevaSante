from django.urls import path
from .views import *

urlpatterns = [
    path("create/", PatientCreateAppointmentView.as_view()),
    path("<int:pk>/cancel/", PatientCancelAppointmentView.as_view()),
    path("reception/create/", ReceptionCreateAppointmentView.as_view()),
    path("doctor/", DoctorAppointmentsView.as_view()),
]