from django.db.models import Q

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from drf_yasg.utils import swagger_auto_schema

from authentication.models import PatientProfile
from .models import DoctorPatient
from .serializers import (
    PatientProfileSerializer,
    PatientListSerializer,
    ReceptionistCreatePatientSerializer,
    DoctorPatientListSerializer,
)
from .permissions import IsPatient, IsReceptionist, IsDoctor


class PatientMyProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsPatient]

    @swagger_auto_schema(
        tags=["Patients"],
        operation_summary="الملف الشخصي للمريض",
        operation_description="RG-003: المريض لا يمكنه الاطلاع إلا على بياناته الشخصية.",
        responses={200: PatientProfileSerializer},
    )
    def get(self, request):
        profile = request.user.patient_profile
        serializer = PatientProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ReceptionistPatientSearchView(generics.ListAPIView):
    serializer_class = PatientListSerializer
    permission_classes = [permissions.IsAuthenticated, IsReceptionist]

    @swagger_auto_schema(
        tags=["Patients"],
        operation_summary="البحث عن المرضى",
        operation_description="يمكن لموظف الاستقبال البحث عن مريض بالاسم أو البريد أو الهاتف أو الرقم الوطني.",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        query = self.request.query_params.get("q", "").strip()
        queryset = PatientProfile.objects.select_related("user").all()

        if query:
            queryset = queryset.filter(
                Q(user__first_name__icontains=query)
                | Q(user__last_name__icontains=query)
                | Q(user__email__icontains=query)
                | Q(user__phone__icontains=query)
                | Q(national_id__icontains=query)
            )

        return queryset.order_by("user__first_name", "user__last_name")


class ReceptionistCreatePatientView(generics.CreateAPIView):
    serializer_class = ReceptionistCreatePatientSerializer
    permission_classes = [permissions.IsAuthenticated, IsReceptionist]

    @swagger_auto_schema(
        tags=["Patients"],
        operation_summary="إضافة مريض جديد",
        operation_description="يمكن لموظف الاستقبال إنشاء مريض جديد في النظام.",
        request_body=ReceptionistCreatePatientSerializer,
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        profile = serializer.save()

        return Response(
            {
                "message": "تمت إضافة المريض بنجاح.",
                "data": PatientProfileSerializer(profile).data,
            },
            status=status.HTTP_201_CREATED,
        )


class DoctorMyPatientsView(generics.ListAPIView):
    serializer_class = DoctorPatientListSerializer
    permission_classes = [permissions.IsAuthenticated, IsDoctor]

    @swagger_auto_schema(
        tags=["Patients"],
        operation_summary="قائمة مرضى الطبيب",
        operation_description="RG-004: الطبيب لا يمكنه الاطلاع إلا على المرضى المرتبطين به.",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return DoctorPatient.objects.select_related(
            "patient",
            "patient__patient_profile",
        ).filter(doctor=self.request.user)