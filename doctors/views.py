from django.shortcuts import render

# Create your views here.
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema

from authentication.models import DoctorProfile
from .serializers import (
    DoctorListSerializer,
    AdminCreateDoctorSerializer,
    DoctorProfileUpdateSerializer,
)
from .permissions import IsAdminUserRole, IsDoctor


class AvailableDoctorsListView(generics.ListAPIView):
    serializer_class = DoctorListSerializer
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        tags=["Doctors"],
        operation_summary="قائمة الأطباء المتاحين",
        operation_description="يمكن للمريض أو أي مستخدم مسجل الاطلاع على قائمة الأطباء المتاحين.",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return DoctorProfile.objects.select_related("user").filter(
            available=True,
            user__is_active=True,
        )


class AdminCreateDoctorView(generics.CreateAPIView):
    serializer_class = AdminCreateDoctorSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUserRole]

    @swagger_auto_schema(
        tags=["Doctors"],
        operation_summary="إضافة طبيب جديد",
        operation_description="يمكن للمدير إنشاء حساب طبيب جديد داخل النظام.",
        request_body=AdminCreateDoctorSerializer,
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response(
            {
                "message": "تم إنشاء حساب الطبيب بنجاح.",
                "data": {
                    "id": user.id,
                    "email": user.email,
                    "full_name": user.full_name,
                    "role": user.role,
                    "is_first_login": user.is_first_login,
                },
            },
            status=status.HTTP_201_CREATED,
        )


class DoctorMyProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsDoctor]

    @swagger_auto_schema(
        tags=["Doctors"],
        operation_summary="ملف الطبيب الحالي",
    )
    def get(self, request):
        profile = request.user.doctor_profile
        serializer = DoctorListSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)


class DoctorUpdateMyProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsDoctor]

    @swagger_auto_schema(
        tags=["Doctors"],
        operation_summary="تعديل ملف الطبيب",
        request_body=DoctorProfileUpdateSerializer,
    )
    def put(self, request):
        profile = request.user.doctor_profile
        serializer = DoctorProfileUpdateSerializer(
            profile,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {
                "message": "تم تحديث ملف الطبيب بنجاح.",
                "data": DoctorListSerializer(profile).data,
            },
            status=status.HTTP_200_OK,
        )