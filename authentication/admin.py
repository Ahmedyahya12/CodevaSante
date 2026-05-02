from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin

from .models import (
    CustomUser,
    PatientProfile,
    DoctorProfile,
    ReceptionistProfile,
    UserRole,
)
from .utils import send_activation_email


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser

    list_display = (
        "email",
        "first_name",
        "last_name",
        "role",
        "is_active",
        "is_staff",
        "is_first_login",
    )

    list_filter = ("role", "is_active", "is_staff", "is_superuser")
    ordering = ("-created_at",)
    search_fields = ("email", "first_name", "last_name", "phone")

    fieldsets = (
        ("بيانات الدخول", {"fields": ("email", "password")}),
        ("المعلومات الشخصية", {"fields": ("first_name", "last_name", "phone")}),
        (
            "الصلاحيات",
            {
                "fields": (
                    "role",
                    "is_first_login",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("تواريخ النظام", {"fields": ("last_login",)}),
    )

    add_fieldsets = (
        (
            "إضافة مستخدم جديد",
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "first_name",
                    "last_name",
                    "phone",
                    "role",
                    "password1",
                    "password2",
                    "is_first_login",
                    "is_active",
                    "is_staff",
                ),
            },
        ),
    )

    filter_horizontal = ("groups", "user_permissions")

    def save_model(self, request, obj, form, change):
        is_new = obj.pk is None

        if is_new and obj.role in [UserRole.DOCTOR, UserRole.RECEPTIONIST]:
            obj.is_first_login = True
            obj.is_active = True

        super().save_model(request, obj, form, change)

        if is_new:
            if obj.role == UserRole.DOCTOR:
                DoctorProfile.objects.get_or_create(user=obj)

            elif obj.role == UserRole.RECEPTIONIST:
                ReceptionistProfile.objects.get_or_create(user=obj)

            elif obj.role == UserRole.PATIENT:
                PatientProfile.objects.get_or_create(user=obj)

            if obj.role in [UserRole.DOCTOR, UserRole.RECEPTIONIST]:
                try:
                    send_activation_email(obj)
                    messages.success(
                        request,
                        f"تم إنشاء الحساب وإرسال رابط تفعيل كلمة المرور إلى {obj.email}.",
                    )
                except Exception as exc:
                    messages.error(
                        request,
                        f"تم إنشاء الحساب لكن فشل إرسال البريد الإلكتروني: {exc}",
                    )


@admin.register(PatientProfile)
class PatientProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "date_of_birth", "gender", "national_id")
    search_fields = (
        "user__email",
        "user__first_name",
        "user__last_name",
        "national_id",
    )


@admin.register(DoctorProfile)
class DoctorProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "specialty", "years_of_experience", "available")
    search_fields = ("user__email", "user__first_name", "user__last_name", "specialty")


@admin.register(ReceptionistProfile)
class ReceptionistProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "active")
    search_fields = ("user__email", "user__first_name", "user__last_name")
