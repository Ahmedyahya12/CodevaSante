from django.urls import path
from .views import TodayAppointmentsView, ConfirmPatientArrivalView

urlpatterns = [
    path("today-appointments/", TodayAppointmentsView.as_view(), name="today-appointments"),
    path("appointments/<int:pk>/confirm-arrival/", ConfirmPatientArrivalView.as_view(), name="confirm-arrival"),
]