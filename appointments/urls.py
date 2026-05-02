from django.urls import path

from appointments.view_1 import DoctorAppointmentStatusUpdateView, DoctorTodayAppointmentsView, DoctorUpcomingAppointmentsView
from .views import *

urlpatterns = [
    path("create/", PatientCreateAppointmentView.as_view()),
    path("my/", PatientAppointmentsView.as_view()),
    path("today/", TodayAppointmentsView.as_view()),
    path("<int:pk>/cancel/", PatientCancelAppointmentView.as_view()),
    path("<int:pk>/confirm/", ConfirmAppointmentView.as_view()),
    path("<int:pk>/check-in/", CheckInAppointmentView.as_view()),
    path("reception/create/", ReceptionCreateAppointmentView.as_view()),
    path("doctor/", DoctorAppointmentsView.as_view()),

    path(
        "doctor/today/",
        DoctorTodayAppointmentsView.as_view(),
        name="doctor-appointments-today",
    ),
    path(
        "doctor/upcoming/",
        DoctorUpcomingAppointmentsView.as_view(),
        name="doctor-appointments-upcoming",
    ),
    path(
        "doctor/<int:pk>/status/",
        DoctorAppointmentStatusUpdateView.as_view(),
        name="doctor-appointment-status",
    ),
]
