from rest_framework import serializers
from django.contrib.auth import get_user_model
from authentication.models import PatientProfile, UserRole
from .models import DoctorPatient

User = get_user_model()


class PatientProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source="user.full_name", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    first_name = serializers.CharField(source="user.first_name", read_only=True)
    last_name = serializers.CharField(source="user.last_name", read_only=True)
    phone = serializers.CharField(source="user.phone", read_only=True)

    class Meta:
        model = PatientProfile
        fields = [
            "id",
            "full_name",
            "email",
            "first_name",
            "last_name",
            "phone",
            "date_of_birth",
            "gender",
            "address",
            "national_id",
            "emergency_contact",
            "medical_notes",
        ]


class PatientListSerializer(serializers.ModelSerializer):
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
            "national_id",
        ]


class ReceptionistCreatePatientSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(write_only=True)
    first_name = serializers.CharField(write_only=True)
    last_name = serializers.CharField(write_only=True)
    phone = serializers.CharField(write_only=True, required=False, allow_blank=True)
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = PatientProfile
        fields = [
            "email",
            "first_name",
            "last_name",
            "phone",
            "password",
            "password_confirm",
            "date_of_birth",
            "gender",
            "address",
            "national_id",
            "emergency_contact",
            "medical_notes",
        ]

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("هذا البريد الإلكتروني مستخدم بالفعل.")
        return value

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError(
                {"password_confirm": "كلمتا المرور غير متطابقتين."}
            )
        return attrs

    def create(self, validated_data):
        email = validated_data.pop("email")
        first_name = validated_data.pop("first_name")
        last_name = validated_data.pop("last_name")
        phone = validated_data.pop("phone", "")
        password = validated_data.pop("password")
        validated_data.pop("password_confirm")

        user = User.objects.create_user(
            email=email,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            password=password,
            role=UserRole.PATIENT,
        )

        profile = user.patient_profile
        profile.date_of_birth = validated_data.get("date_of_birth")
        profile.gender = validated_data.get("gender", "")
        profile.address = validated_data.get("address", "")
        profile.national_id = validated_data.get("national_id", "")
        profile.emergency_contact = validated_data.get("emergency_contact", "")
        profile.medical_notes = validated_data.get("medical_notes", "")
        profile.save()

        return profile


class DoctorPatientListSerializer(serializers.ModelSerializer):
    patient_id = serializers.IntegerField(source="patient.id", read_only=True)
    full_name = serializers.CharField(source="patient.full_name", read_only=True)
    email = serializers.EmailField(source="patient.email", read_only=True)
    phone = serializers.CharField(source="patient.phone", read_only=True)
    first_name = serializers.CharField(source="patient.first_name", read_only=True)
    last_name = serializers.CharField(source="patient.last_name", read_only=True)
    profile_id = serializers.IntegerField(source="patient.patient_profile.id", read_only=True)
    date_of_birth = serializers.DateField(source="patient.patient_profile.date_of_birth", read_only=True)
    gender = serializers.CharField(source="patient.patient_profile.gender", read_only=True)
    national_id = serializers.CharField(source="patient.patient_profile.national_id", read_only=True)

    class Meta:
        model = DoctorPatient
        fields = [
            "id",
            "patient_id",
            "profile_id",
            "full_name",
            "first_name",
            "last_name",
            "email",
            "phone",
            "date_of_birth",
            "gender",
            "national_id",
            "created_at",
        ]