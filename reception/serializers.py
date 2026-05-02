from rest_framework import serializers

from authentication.models import CustomUser
from appointments.models import Appointment


class ReceptionUserSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = CustomUser
        fields = [
            "id",
            "full_name",
            "email",
            "phone",
        ]


class ReceptionAppointmentSerializer(serializers.ModelSerializer):
    patient = ReceptionUserSerializer(read_only=True)
    doctor = ReceptionUserSerializer(read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = Appointment
        fields = [
            "id",
            "patient",
            "doctor",
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
