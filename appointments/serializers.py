from rest_framework import serializers
from authentication.models import UserRole
from .models import Appointment


class AppointmentSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source="patient.full_name", read_only=True)
    doctor_name = serializers.CharField(source="doctor.full_name", read_only=True)

    class Meta:
        model = Appointment
        fields = "__all__"


class CreateAppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ["doctor", "date", "time", "reason"]

    def validate_doctor(self, value):
        if value.role != UserRole.DOCTOR:
            raise serializers.ValidationError("المستخدم المحدد ليس طبيبًا.")
        if not value.is_active:
            raise serializers.ValidationError("هذا الطبيب غير نشط.")
        return value

    def validate(self, attrs):
        if not attrs.get("doctor"):
            raise serializers.ValidationError({"doctor": "الطبيب مطلوب."})
        if not attrs.get("date"):
            raise serializers.ValidationError({"date": "تاريخ الموعد مطلوب."})
        if not attrs.get("time"):
            raise serializers.ValidationError({"time": "وقت الموعد مطلوب."})
        return attrs

    def create(self, validated_data):
        request = self.context["request"]
        validated_data["patient"] = request.user
        return super().create(validated_data)


class ReceptionCreateAppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Appointment
        fields = ["patient", "doctor", "date", "time", "reason"]

    def validate_patient(self, value):
        if value.role != UserRole.PATIENT:
            raise serializers.ValidationError("المستخدم المحدد ليس مريضًا.")
        if not value.is_active:
            raise serializers.ValidationError("هذا المريض غير نشط.")
        return value

    def validate_doctor(self, value):
        if value.role != UserRole.DOCTOR:
            raise serializers.ValidationError("المستخدم المحدد ليس طبيبًا.")
        if not value.is_active:
            raise serializers.ValidationError("هذا الطبيب غير نشط.")
        return value

    def validate(self, attrs):
        if not attrs.get("patient"):
            raise serializers.ValidationError({"patient": "المريض مطلوب."})
        if not attrs.get("doctor"):
            raise serializers.ValidationError({"doctor": "الطبيب مطلوب."})
        if not attrs.get("date"):
            raise serializers.ValidationError({"date": "تاريخ الموعد مطلوب."})
        if not attrs.get("time"):
            raise serializers.ValidationError({"time": "وقت الموعد مطلوب."})
        return attrs