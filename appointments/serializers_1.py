from rest_framework import serializers

from authentication.models import CustomUser
from .models import Appointment, AppointmentStatus


class AppointmentPatientSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = CustomUser
        fields = [
            "id",
            "full_name",
            "email",
            "phone",
        ]


class DoctorAppointmentSerializer(serializers.ModelSerializer):
    patient = AppointmentPatientSerializer(read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = Appointment
        fields = [
            "id",
            "patient",
            "appointment_date",
            "appointment_time",
            "reason",
            "department",
            "visit_type",
            "status",
            "status_display",
            "price",
            "created_at",
        ]


class AppointmentStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ["status"]

    def validate_status(self, value):
        allowed_statuses = [
            AppointmentStatus.PENDING,
            AppointmentStatus.CONFIRMED,
            AppointmentStatus.COMPLETED,
            AppointmentStatus.CANCELLED,
        ]

        if value not in allowed_statuses:
            raise serializers.ValidationError("حالة الموعد غير صحيحة.")

        return value
