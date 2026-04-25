from django.shortcuts import render

# Create your views here.
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

    @swagger_auto_schema(
        tags=["Reception"],
        operation_summary="قائمة مواعيد اليوم",
        operation_description="REC-001: يمكن لموظف الاستقبال الاطلاع على مواعيد اليوم.",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        today = timezone.localdate()
        return Appointment.objects.select_related(
            "patient",
            "doctor",
        ).filter(date=today).order_by("time")


class ConfirmPatientArrivalView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsReceptionist]

    @swagger_auto_schema(
        tags=["Reception"],
        operation_summary="تأكيد حضور المريض",
        operation_description="REC-002: يمكن لموظف الاستقبال تأكيد حضور المريض عند وصوله.",
    )
    def post(self, request, pk):
        try:
            appointment = Appointment.objects.get(pk=pk)
        except Appointment.DoesNotExist:
            return Response(
                {"message": "الموعد غير موجود."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if appointment.status == AppointmentStatus.CANCELLED:
            return Response(
                {"message": "لا يمكن تأكيد حضور موعد ملغى."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if appointment.status == AppointmentStatus.CHECKED_IN:
            return Response(
                {"message": "تم تأكيد حضور هذا المريض مسبقًا."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        appointment.status = AppointmentStatus.CHECKED_IN
        appointment.save()

        return Response(
            {
                "message": "تم تأكيد حضور المريض بنجاح.",
                "data": ReceptionAppointmentSerializer(appointment).data,
            },
            status=status.HTTP_200_OK,
        )