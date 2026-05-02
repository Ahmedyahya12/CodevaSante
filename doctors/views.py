from django.shortcuts import render
from django.db.models import Count
from django.db.models import Q

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


from django.shortcuts import get_object_or_404

from datetime import datetime, time, timedelta
from appointments.models import Appointment, AppointmentStatus

from .models import DoctorWorkingHour


class DoctorAvailabilityView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, pk):
        date_str = request.query_params.get("date")

        if not date_str:
            return Response({"error": "date is required"}, status=400)

        try:
            selected_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return Response(
                {"error": "invalid date format. Use YYYY-MM-DD"}, status=400
            )

        doctor_profile = get_object_or_404(
            DoctorProfile,
            user__id=pk,
            available=True,
            user__is_active=True,
        )

        day_of_week = selected_date.weekday()

        working_hours = DoctorWorkingHour.objects.filter(
            doctor=doctor_profile,
            day_of_week=day_of_week,
            is_active=True,
        ).order_by("start_time")

        if not working_hours.exists():
            return Response(
                {
                    "doctor": doctor_profile.user.id,
                    "date": str(selected_date),
                    "available_times": [],
                    "message": "الطبيب غير متاح في هذا اليوم.",
                }
            )

        booked_counts = (
            Appointment.objects.filter(
                doctor=doctor_profile.user,
                date=selected_date,
            )
            .exclude(status=AppointmentStatus.CANCELLED)
            .values("time")
            .annotate(total=Count("id"))
        )

        booked_map = {
            item["time"].strftime("%H:%M"): item["total"] for item in booked_counts
        }

        available_times = []
        slot_duration = 60  # كل slot ساعة واحدة: 08:00, 09:00

        for work in working_hours:
            current = datetime.combine(selected_date, work.start_time)
            end = datetime.combine(selected_date, work.end_time)

            while current < end:
                slot = current.time().strftime("%H:%M")
                booked_count = booked_map.get(slot, 0)

                if booked_count < work.max_patients_per_slot:
                    available_times.append(slot)

                current += timedelta(minutes=slot_duration)

        return Response(
            {
                "doctor": doctor_profile.user.id,
                "date": str(selected_date),
                "day_of_week": day_of_week,
                "available_times": available_times,
                "booked_counts": booked_map,
            }
        )


class DoctorDetailView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, pk):
        doctor = get_object_or_404(
            DoctorProfile.objects.select_related("user"),
            user__id=pk,
            user__is_active=True,
        )

        serializer = DoctorListSerializer(
            doctor,
            context={"request": request},
        )

        return Response(serializer.data)


class DoctorSpecialtiesView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):

        specialties = (
            DoctorProfile.objects.exclude(specialty="")
            .values_list("specialty", flat=True)
            .distinct()
        )
        return Response(list(specialties))


class AvailableDoctorsListView(generics.ListAPIView):
    serializer_class = DoctorListSerializer
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        tags=["Doctors"],
        operation_summary="قائمة الأطباء المتاحين",
        operation_description="يمكن للمريض أو أي مستخدم مسجل الاطلاع على قائمة الأطباء المتاحين مع البحث والتصفية حسب التخصص.",
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        queryset = DoctorProfile.objects.select_related("user").filter(
            available=True,
            user__is_active=True,
        )

        specialty = self.request.query_params.get("specialty")
        search = self.request.query_params.get("search")

        if specialty:
            queryset = queryset.filter(specialty=specialty)

        if search:
            queryset = queryset.filter(
                Q(user__first_name__icontains=search)
                | Q(user__last_name__icontains=search)
                | Q(user__email__icontains=search)
                | Q(user__phone__icontains=search)
                | Q(specialty__icontains=search)
                | Q(bio__icontains=search)
            )

        return queryset


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
    http_method_names = ["get", "patch", "put"]

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
