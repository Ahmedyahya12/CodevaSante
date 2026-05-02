from django.db.models import Sum
from django.utils import timezone

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions

from drf_yasg.utils import swagger_auto_schema

from appointments.models import Appointment
from patients.models import DoctorPatient
from appointments.permissions import IsDoctor


from appointments.models import Appointment
from authentication.models import CustomUser, UserRole
from reception.permissions import IsReceptionist


class ReceptionDashboardStatsView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsReceptionist]

    def get(self, request):
        today = timezone.localdate()

        appointments = Appointment.objects.all()

        return Response(
            {
                "today_appointments": appointments.filter(
                    appointment_date=today
                ).count(),
                "pending_appointments": appointments.filter(status="pending").count(),
                "confirmed_appointments": appointments.filter(
                    status="confirmed"
                ).count(),
                "cancelled_appointments": appointments.filter(
                    status="cancelled"
                ).count(),
                "patients_count": CustomUser.objects.filter(
                    role=UserRole.PATIENT
                ).count(),
                "doctors_count": CustomUser.objects.filter(
                    role=UserRole.DOCTOR
                ).count(),
            }
        )


class DoctorDashboardStatsView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsDoctor]

    @swagger_auto_schema(
        tags=["Doctor Dashboard"],
        operation_summary="إحصائيات لوحة تحكم الطبيب",
    )
    def get(self, request):
        doctor = request.user
        today = timezone.localdate()

        appointments_qs = Appointment.objects.filter(doctor=doctor)

        total_appointments = appointments_qs.count()

        today_appointments = appointments_qs.filter(appointment_date=today).count()

        upcoming_appointments = (
            appointments_qs.filter(appointment_date__gte=today)
            .exclude(status="cancelled")
            .count()
        )

        completed_appointments = appointments_qs.filter(status="completed").count()

        cancelled_appointments = appointments_qs.filter(status="cancelled").count()

        patients_count = DoctorPatient.objects.filter(doctor=doctor).count()

        revenue = (
            appointments_qs.filter(status="completed").aggregate(total=Sum("price"))[
                "total"
            ]
            or 0
        )

        next_appointment = (
            appointments_qs.select_related("patient")
            .filter(appointment_date__gte=today)
            .exclude(status="cancelled")
            .order_by("appointment_date", "appointment_time")
            .first()
        )

        next_appointment_data = None

        if next_appointment:
            next_appointment_data = {
                "id": next_appointment.id,
                "patient_name": next_appointment.patient.full_name,
                "patient_phone": next_appointment.patient.phone,
                "date": next_appointment.appointment_date,
                "time": next_appointment.appointment_time,
                "department": next_appointment.department,
                "visit_type": next_appointment.visit_type,
                "status": next_appointment.status,
            }

        return Response(
            {
                "total_appointments": total_appointments,
                "today_appointments": today_appointments,
                "upcoming_appointments": upcoming_appointments,
                "completed_appointments": completed_appointments,
                "cancelled_appointments": cancelled_appointments,
                "patients_count": patients_count,
                "online_consultations": 0,
                "revenue": revenue,
                "next_appointment": next_appointment_data,
            }
        )
