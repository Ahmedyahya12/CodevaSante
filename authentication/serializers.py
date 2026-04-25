from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import (
    CustomUser,
    UserRole,
    PatientProfile,
)


class PatientRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)

    date_of_birth = serializers.DateField(required=False, allow_null=True)
    gender = serializers.ChoiceField(
        choices=PatientProfile.GENDER_CHOICES,
        required=False,
        allow_blank=True,
    )
    address = serializers.CharField(required=False, allow_blank=True)
    national_id = serializers.CharField(required=False, allow_blank=True)
    emergency_contact = serializers.CharField(required=False, allow_blank=True)
    medical_notes = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = CustomUser
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
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("هذا البريد الإلكتروني مستخدم بالفعل.")
        return value

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError(
                {"password_confirm": "كلمتا المرور غير متطابقتين."}
            )
        return attrs

    def create(self, validated_data):
        profile_data = {
            "date_of_birth": validated_data.pop("date_of_birth", None),
            "gender": validated_data.pop("gender", ""),
            "address": validated_data.pop("address", ""),
            "national_id": validated_data.pop("national_id", ""),
            "emergency_contact": validated_data.pop("emergency_contact", ""),
            "medical_notes": validated_data.pop("medical_notes", ""),
        }

        password = validated_data.pop("password")
        validated_data.pop("password_confirm")

        user = CustomUser.objects.create_user(
            email=validated_data["email"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            phone=validated_data.get("phone", ""),
            password=password,
            role=UserRole.PATIENT,
            is_first_login=False,
        )

        profile = user.patient_profile
        profile.date_of_birth = profile_data["date_of_birth"]
        profile.gender = profile_data["gender"]
        profile.address = profile_data["address"]
        profile.national_id = profile_data["national_id"]
        profile.emergency_contact = profile_data["emergency_contact"]
        profile.medical_notes = profile_data["medical_notes"]
        profile.save()

        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = "email"

    def validate(self, attrs):
        user = authenticate(
            request=self.context.get("request"),
            username=attrs.get("email"),
            password=attrs.get("password"),
        )

        if user is None:
            raise serializers.ValidationError("البريد الإلكتروني أو كلمة المرور غير صحيحة.")

        if not user.is_active:
            raise serializers.ValidationError("هذا الحساب غير مفعل.")

        data = super().validate(attrs)

        data["user"] = {
            "id": self.user.id,
            "email": self.user.email,
            "first_name": self.user.first_name,
            "last_name": self.user.last_name,
            "full_name": self.user.full_name,
            "phone": self.user.phone,
            "role": self.user.role,
            "role_display": self.user.get_role_display(),
            "is_first_login": self.user.is_first_login,
        }

        return data


class CurrentUserSerializer(serializers.ModelSerializer):
    role_display = serializers.CharField(source="get_role_display", read_only=True)
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = CustomUser
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "full_name",
            "phone",
            "role",
            "role_display",
            "is_first_login",
        ]


class FirstLoginSetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError(
                {"confirm_password": "كلمتا المرور غير متطابقتين."}
            )
        return attrs


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError(
                {"confirm_password": "كلمتا المرور غير متطابقتين."}
            )
        return attrs