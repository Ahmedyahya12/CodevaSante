from django.urls import path
from .views import (
    TodayAppointmentsView,
    ReceptionAppointmentsView,
    ReceptionAppointmentStatusUpdateView,
    ConfirmPatientArrivalView,
)

urlpatterns = [
    path(
        "appointments/",
        ReceptionAppointmentsView.as_view(),
        name="reception-appointments",
    ),
    path(
        "today-appointments/",
        TodayAppointmentsView.as_view(),
        name="today-appointments",
    ),
    path(
        "appointments/<int:pk>/status/",
        ReceptionAppointmentStatusUpdateView.as_view(),
        name="reception-appointment-status",
    ),
    path(
        "appointments/<int:pk>/confirm-arrival/",
        ConfirmPatientArrivalView.as_view(),
        name="confirm-arrival",
    ),
]
