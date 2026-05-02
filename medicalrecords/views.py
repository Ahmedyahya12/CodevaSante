from django.shortcuts import render

# Create your views here.
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema

from .models import MedicalRecord
from .serializers import (
    MedicalRecordSerializer,
    CreateMedicalRecordSerializer,
)
from .permissions import IsDoctor, IsPatient
from patients.models import DoctorPatient


# MED-001
class DoctorCreateMedicalRecordView(generics.CreateAPIView):
    serializer_class = CreateMedicalRecordSerializer
    permission_classes = [permissions.IsAuthenticated, IsDoctor]

    @swagger_auto_schema(tags=["MedicalRecords"])
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        patient = serializer.validated_data["patient"]

        # # RG-004: تحقق أن المريض تابع للطبيب
        # if not DoctorPatient.objects.filter(
        #     doctor=request.user,
        #     patient=patient
        # ).exists():
        #     return Response(
        #         {"message": "غير مصرح: هذا المريض ليس ضمن مرضاك."},
        #         status=403,
        #     )

        record = MedicalRecord.objects.create(
            patient=patient,
            doctor=request.user,
            note=serializer.validated_data["note"],
        )

        return Response(
            {
                "message": "تمت إضافة الملاحظة الطبية بنجاح.",
                "data": MedicalRecordSerializer(record).data,
            },
            status=status.HTTP_201_CREATED,
        )


# MED-002
class DoctorPatientRecordsView(generics.ListAPIView):
    serializer_class = MedicalRecordSerializer
    permission_classes = [permissions.IsAuthenticated, IsDoctor]

    @swagger_auto_schema(tags=["MedicalRecords"])
    def get_queryset(self):
        patient_id = self.request.query_params.get("patient_id")

        return MedicalRecord.objects.filter(
            doctor=self.request.user,
            patient_id=patient_id
        )


# MED-003
class PatientMyRecordsView(generics.ListAPIView):
    serializer_class = MedicalRecordSerializer
    permission_classes = [permissions.IsAuthenticated, IsPatient]

    @swagger_auto_schema(tags=["MedicalRecords"])
    def get_queryset(self):
        return MedicalRecord.objects.filter(patient=self.request.user)
