from rest_framework import serializers
from appointments.models import Appointment


class ReceptionAppointmentSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source="patient.full_name", read_only=True)
    patient_email = serializers.EmailField(source="patient.email", read_only=True)
    patient_phone = serializers.CharField(source="patient.phone", read_only=True)

    doctor_name = serializers.CharField(source="doctor.full_name", read_only=True)
    doctor_email = serializers.EmailField(source="doctor.email", read_only=True)

    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = Appointment
        fields = [
            "id",
            "patient",
            "patient_name",
            "patient_email",
            "patient_phone",
            "doctor",
            "doctor_name",
            "doctor_email",
            "date",
            "time",
            "reason",
            "status",
            "status_display",
            "created_at",  
        ]