from django.contrib import admin
from .models import Appointment, AppointmentStatus


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "patient",
        "doctor",
        "appointment_date",
        "appointment_time",
        "status",
        "price",
        "created_at",
    )

    list_filter = (
        "status",
        "appointment_date",
        "doctor",
    )

    search_fields = (
        "patient__email",
        "patient__first_name",
        "patient__last_name",
        "doctor__email",
        "doctor__first_name",
        "doctor__last_name",
        "reason",
        "department",
        "visit_type",
    )

    ordering = ("-appointment_date", "-appointment_time")

    readonly_fields = ("created_at",)

    fieldsets = (
        (
            "معلومات الموعد",
            {
                "fields": (
                    "patient",
                    "doctor",
                    "appointment_date",
                    "appointment_time",
                    "status",
                )
            },
        ),
        (
            "تفاصيل إضافية",
            {
                "fields": (
                    "reason",
                    "department",
                    "visit_type",
                    "price",
                )
            },
        ),
        (
            "معلومات النظام",
            {
                "fields": ("created_at",),
            },
        ),
    )

    actions = [
        "mark_as_pending",
        "mark_as_confirmed",
        "mark_as_completed",
        "mark_as_cancelled",
    ]

    @admin.action(description="إرجاع المواعيد إلى قيد الانتظار")
    def mark_as_pending(self, request, queryset):
        queryset.update(status=AppointmentStatus.PENDING)

    @admin.action(description="تأكيد المواعيد المحددة")
    def mark_as_confirmed(self, request, queryset):
        queryset.update(status=AppointmentStatus.CONFIRMED)

    @admin.action(description="تحديد المواعيد كمكتملة")
    def mark_as_completed(self, request, queryset):
        queryset.update(status=AppointmentStatus.COMPLETED)

    @admin.action(description="إلغاء المواعيد المحددة")
    def mark_as_cancelled(self, request, queryset):
        queryset.update(status=AppointmentStatus.CANCELLED)
