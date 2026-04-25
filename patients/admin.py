from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import DoctorPatient


@admin.register(DoctorPatient)
class DoctorPatientAdmin(admin.ModelAdmin):
    list_display = ("doctor", "patient", "created_at")
    search_fields = (
        "doctor__email",
        "doctor__first_name",
        "doctor__last_name",
        "patient__email",
        "patient__first_name",
        "patient__last_name",
    )
    list_filter = ("created_at",)