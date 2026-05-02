# patients/serializers.py

from rest_framework import serializers

from authentication.models import CustomUser, PatientProfile, UserRole
from authentication.utils import send_patient_activation_email
from .models import DoctorPatient


class ReceptionistCreatePatientSerializer(serializers.Serializer):
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    phone = serializers.CharField(required=False, allow_blank=True)

    gender = serializers.CharField(required=False, allow_blank=True)
    address = serializers.CharField(required=False, allow_blank=True)
    national_id = serializers.CharField(required=False, allow_blank=True)

    emergency_contact = serializers.CharField(required=False, allow_blank=True)
    medical_notes = serializers.CharField(required=False, allow_blank=True)
    date_of_birth = serializers.DateField(required=False, allow_null=True)

    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("هذا البريد الإلكتروني مستخدم بالفعل.")
        return value

    def create(self, validated_data):
        profile_data = {
            "gender": validated_data.pop("gender", ""),
            "address": validated_data.pop("address", ""),
            "national_id": validated_data.pop("national_id", ""),
            "emergency_contact": validated_data.pop("emergency_contact", ""),
            "medical_notes": validated_data.pop("medical_notes", ""),
            "date_of_birth": validated_data.pop("date_of_birth", None),
        }

        user = CustomUser.objects.create(
            email=validated_data["email"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            phone=validated_data.get("phone", ""),
            role=UserRole.PATIENT,
            is_active=True,
        )

        user.set_unusable_password()
        user.save()

        profile, _ = PatientProfile.objects.get_or_create(
            user=user,
            defaults=profile_data,
        )

        send_patient_activation_email(user)

        return profile


class PatientProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source="user.full_name", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    phone = serializers.CharField(source="user.phone", read_only=True)

    class Meta:
        model = PatientProfile
        fields = [
            "id",
            "full_name",
            "email",
            "phone",
            "date_of_birth",
            "gender",
            "address",
            "national_id",
            "emergency_contact",
            "medical_notes",
            "created_at",
        ]


class PatientListSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="user.id", read_only=True)
    full_name = serializers.CharField(source="user.full_name", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    phone = serializers.CharField(source="user.phone", read_only=True)

    class Meta:
        model = PatientProfile
        fields = [
            "id",
            "full_name",
            "email",
            "phone",
            "gender",
            "national_id",
            "address",
            "created_at",
        ]


class DoctorPatientUserSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    full_name = serializers.CharField()
    email = serializers.EmailField()
    phone = serializers.CharField(allow_blank=True, required=False)


class DoctorPatientListSerializer(serializers.ModelSerializer):
    patient = DoctorPatientUserSerializer(read_only=True)

    class Meta:
        model = DoctorPatient
        fields = [
            "id",
            "patient",
            "created_at",
        ]
