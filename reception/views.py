from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema

from appointments.models import Appointment, AppointmentStatus
from .serializers import ReceptionAppointmentSerializer
from .permissions import IsReceptionist


class TodayAppointmentsView(generics.ListAPIView):
    serializer_class = ReceptionAppointmentSerializer
    permission_classes = [permissions.IsAuthenticated, IsReceptionist]

    @swagger_auto_schema(tags=["Reception"], operation_summary="قائمة مواعيد اليوم")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        today = timezone.localdate()
        return (
            Appointment.objects.select_related("patient", "doctor")
            .filter(appointment_date=today)
            .order_by("appointment_time")
        )


class ReceptionAppointmentsView(generics.ListAPIView):
    serializer_class = ReceptionAppointmentSerializer
    permission_classes = [permissions.IsAuthenticated, IsReceptionist]

    def get_queryset(self):
        return (
            Appointment.objects.select_related("patient", "doctor")
            .all()
            .order_by("-appointment_date", "-appointment_time")
        )


class ReceptionAppointmentStatusUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsReceptionist]

    def patch(self, request, pk):
        try:
            appointment = Appointment.objects.select_related("patient", "doctor").get(
                pk=pk
            )
        except Appointment.DoesNotExist:
            return Response({"message": "الموعد غير موجود."}, status=404)

        new_status = request.data.get("status")

        allowed = [
            AppointmentStatus.PENDING,
            AppointmentStatus.CONFIRMED,
            AppointmentStatus.CANCELLED,
        ]

        if new_status not in allowed:
            return Response(
                {"message": "موظف الاستقبال يمكنه فقط تأكيد أو إلغاء الموعد."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        appointment.status = new_status
        appointment.save()

        return Response(
            {
                "message": "تم تحديث حالة الموعد بنجاح.",
                "data": ReceptionAppointmentSerializer(appointment).data,
            },
            status=status.HTTP_200_OK,
        )


class ConfirmPatientArrivalView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsReceptionist]

    def post(self, request, pk):
        try:
            appointment = Appointment.objects.select_related("patient", "doctor").get(
                pk=pk
            )
        except Appointment.DoesNotExist:
            return Response({"message": "الموعد غير موجود."}, status=404)

        if appointment.status == AppointmentStatus.CANCELLED:
            return Response(
                {"message": "لا يمكن تأكيد حضور موعد ملغى."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        appointment.status = AppointmentStatus.CONFIRMED
        appointment.save()

        return Response(
            {
                "message": "تم تأكيد حضور المريض بنجاح.",
                "data": ReceptionAppointmentSerializer(appointment).data,
            },
            status=status.HTTP_200_OK,
        )
