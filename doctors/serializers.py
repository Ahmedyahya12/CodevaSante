from rest_framework import serializers
from django.contrib.auth import get_user_model
from authentication.models import DoctorProfile, UserRole

User = get_user_model()




class DoctorListSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="user.id", read_only=True)
    full_name = serializers.CharField(source="user.full_name", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    phone = serializers.CharField(source="user.phone", read_only=True)
    image = serializers.SerializerMethodField()

    class Meta:
        model = DoctorProfile
        fields = [
            "id",
            "full_name",
            "email",
            "phone",
            "specialty",
            "bio",
            "years_of_experience",
            "available",
            "max_patients_per_slot",
            "image",
        ]

    def get_image(self, obj):
        request = self.context.get("request")

        if not obj.image:
            return None

        image_url = obj.image.url

        if request:
            return request.build_absolute_uri(image_url)

        return image_url


class AdminCreateDoctorSerializer(serializers.Serializer):
    email = serializers.EmailField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    phone = serializers.CharField(required=False, allow_blank=True)
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)

    specialty = serializers.CharField(required=False, allow_blank=True)
    bio = serializers.CharField(required=False, allow_blank=True)
    years_of_experience = serializers.IntegerField(required=False, default=0)
    available = serializers.BooleanField(required=False, default=True)

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("هذا البريد الإلكتروني مستخدم بالفعل.")
        return value

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError({
                "password_confirm": "كلمتا المرور غير متطابقتين."
            })
        return attrs

    def create(self, validated_data):
        specialty = validated_data.pop("specialty", "")
        bio = validated_data.pop("bio", "")
        years = validated_data.pop("years_of_experience", 0)
        available = validated_data.pop("available", True)
        validated_data.pop("password_confirm")

        password = validated_data.pop("password")

        user = User.objects.create_user(
            email=validated_data["email"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            phone=validated_data.get("phone", ""),
            password=password,
            role=UserRole.DOCTOR,
            is_first_login=True,
        )

        profile = user.doctor_profile
        profile.specialty = specialty
        profile.bio = bio
        profile.years_of_experience = years
        profile.available = available
        profile.save()

        return user


class DoctorProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DoctorProfile
        fields = [
            "specialty",
            "bio",
            "years_of_experience",
            "available",
            "max_patients_per_slot",
            "image",
        ]
