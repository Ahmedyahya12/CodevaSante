from django.urls import path
from .views import DoctorDashboardStatsView, ReceptionDashboardStatsView

urlpatterns = [
    path(
        "doctor/stats/",
        DoctorDashboardStatsView.as_view(),
        name="doctor-dashboard-stats",
    ),
    path("reception/stats/", ReceptionDashboardStatsView.as_view()),
]
