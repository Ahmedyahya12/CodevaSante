from django.utils import timezone

from rest_framework import generics, permissions, status
from rest_framework.response import Response

from drf_yasg.utils import swagger_auto_schema

from .models import Appointment
from .serializers_1 import (
    DoctorAppointmentSerializer,
    AppointmentStatusUpdateSerializer,
)
from .permissions import IsDoctor


class DoctorAppointmentsView(generics.ListAPIView):
    serializer_class = DoctorAppointmentSerializer
    permission_classes = [permissions.IsAuthenticated, IsDoctor]

    @swagger_auto_schema(
        tags=["Doctor Appointments"],
        operation_summary="قائمة مواعيد الطبيب",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return (
            Appointment.objects
            .select_related("patient", "doctor")
            .filter(doctor=self.request.user)
            .order_by("-appointment_date", "-appointment_time")
        )


class DoctorTodayAppointmentsView(generics.ListAPIView):
    serializer_class = DoctorAppointmentSerializer
    permission_classes = [permissions.IsAuthenticated, IsDoctor]

    @swagger_auto_schema(
        tags=["Doctor Appointments"],
        operation_summary="مواعيد الطبيب اليوم",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        today = timezone.localdate()

        return (
            Appointment.objects
            .select_related("patient", "doctor")
            .filter(
                doctor=self.request.user,
                appointment_date=today,
            )
            .order_by("appointment_time")
        )


class DoctorUpcomingAppointmentsView(generics.ListAPIView):
    serializer_class = DoctorAppointmentSerializer
    permission_classes = [permissions.IsAuthenticated, IsDoctor]

    @swagger_auto_schema(
        tags=["Doctor Appointments"],
        operation_summary="المواعيد القادمة للطبيب",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        today = timezone.localdate()

        return (
            Appointment.objects
            .select_related("patient", "doctor")
            .filter(
                doctor=self.request.user,
                appointment_date__gte=today,
            )
            .exclude(status="cancelled")
            .order_by("appointment_date", "appointment_time")
        )


class DoctorAppointmentStatusUpdateView(generics.UpdateAPIView):
    serializer_class = AppointmentStatusUpdateSerializer
    permission_classes = [permissions.IsAuthenticated, IsDoctor]
    http_method_names = ["patch"]

    @swagger_auto_schema(
        tags=["Doctor Appointments"],
        operation_summary="تحديث حالة الموعد",
        request_body=AppointmentStatusUpdateSerializer,
    )
    def patch(self, request, *args, **kwargs):
        appointment = self.get_object()
        serializer = self.get_serializer(
            appointment,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {
                "message": "تم تحديث حالة الموعد بنجاح.",
                "data": DoctorAppointmentSerializer(appointment).data,
            },
            status=status.HTTP_200_OK,
        )

    def get_queryset(self):
        return Appointment.objects.filter(doctor=self.request.user)
