from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, PatientProfile, DoctorProfile, ReceptionistProfile


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
