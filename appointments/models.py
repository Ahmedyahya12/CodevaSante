from django.conf import settings
from django.db import models


class AppointmentStatus(models.TextChoices):
    PENDING = "pending", "قيد الانتظار"
    CONFIRMED = "confirmed", "مؤكد"
    COMPLETED = "completed", "مكتمل"
    CANCELLED = "cancelled", "ملغى"


class Appointment(models.Model):
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="doctor_appointments",
        verbose_name="الطبيب",
    )
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="patient_appointments",
        verbose_name="المريض",
    )
    appointment_date = models.DateField(verbose_name="تاريخ الموعد")
    appointment_time = models.TimeField(verbose_name="وقت الموعد")

    reason = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="سبب الزيارة",
    )
    department = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="القسم",
    )
    visit_type = models.CharField(
        max_length=150,
        default="استشارة عامة",
        verbose_name="نوع الزيارة",
    )

    status = models.CharField(
        max_length=20,
        choices=AppointmentStatus.choices,
        default=AppointmentStatus.PENDING,
        verbose_name="الحالة",
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="السعر",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["appointment_date", "appointment_time"]
        verbose_name = "موعد"
        verbose_name_plural = "المواعيد"

    def __str__(self):
        return f"{self.patient.email} مع {self.doctor.email}"
