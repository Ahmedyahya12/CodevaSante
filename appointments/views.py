from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema

from .models import Appointment, AppointmentStatus
from .serializers import (
    AppointmentSerializer,
    CreateAppointmentSerializer,
    ReceptionCreateAppointmentSerializer,
)
from .permissions import IsPatient, IsReceptionist, IsDoctor


class PatientCreateAppointmentView(generics.CreateAPIView):
    serializer_class = CreateAppointmentSerializer
    permission_classes = [permissions.IsAuthenticated, IsPatient]

    @swagger_auto_schema(
        tags=["Appointments"],
        operation_summary="حجز موعد من طرف المريض",
        request_body=CreateAppointmentSerializer,
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        appointment = serializer.save()

        return Response(
            {
                "message": "تم حجز الموعد بنجاح.",
                "data": AppointmentSerializer(appointment).data,
            },
            status=status.HTTP_201_CREATED,
        )


class PatientCancelAppointmentView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsPatient]

    @swagger_auto_schema(
        tags=["Appointments"],
        operation_summary="إلغاء موعد من طرف المريض",
    )
    def post(self, request, pk):
        try:
            appointment = Appointment.objects.get(id=pk, patient=request.user)
        except Appointment.DoesNotExist:
            return Response(
                {"message": "الموعد غير موجود أو لا تملك صلاحية إلغائه."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if appointment.status == AppointmentStatus.CANCELLED:
            return Response(
                {"message": "هذا الموعد ملغى مسبقًا."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        appointment.status = AppointmentStatus.CANCELLED
        appointment.save()

        return Response(
            {"message": "تم إلغاء الموعد بنجاح."},
            status=status.HTTP_200_OK,
        )


class ReceptionCreateAppointmentView(generics.CreateAPIView):
    serializer_class = ReceptionCreateAppointmentSerializer
    permission_classes = [permissions.IsAuthenticated, IsReceptionist]

    @swagger_auto_schema(
        tags=["Appointments"],
        operation_summary="إنشاء موعد من طرف الاستقبال",
        request_body=ReceptionCreateAppointmentSerializer,
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        appointment = serializer.save()

        return Response(
            {
                "message": "تم إنشاء الموعد بنجاح من طرف الاستقبال.",
                "data": AppointmentSerializer(appointment).data,
            },
            status=status.HTTP_201_CREATED,
        )


class DoctorAppointmentsView(generics.ListAPIView):
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.IsAuthenticated, IsDoctor]

    @swagger_auto_schema(
        tags=["Appointments"],
        operation_summary="قائمة مواعيد الطبيب",
        operation_description="RG-004: الطبيب لا يمكنه الاطلاع إلا على مواعيده ومرضاه المرتبطين به.",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return Appointment.objects.filter(doctor=self.request.user).select_related(
            "patient",
            "doctor",
        )