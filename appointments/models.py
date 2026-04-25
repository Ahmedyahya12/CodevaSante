from django.conf import settings
from django.db import models


class AppointmentStatus(models.TextChoices):
    PENDING = "pending", "قيد الانتظار"
    CONFIRMED = "confirmed", "مؤكد"
    CHECKED_IN = "checked_in", "حضر إلى العيادة"
    CANCELLED = "cancelled", "ملغى"

class Appointment(models.Model):
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="appointments",
        verbose_name="المريض",
    )
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="doctor_appointments",
        verbose_name="الطبيب",
    )
    date = models.DateField(verbose_name="تاريخ الموعد")
    time = models.TimeField(verbose_name="وقت الموعد")
    reason = models.TextField(blank=True, verbose_name="سبب الزيارة")
    status = models.CharField(
        max_length=20,
        choices=AppointmentStatus.choices,
        default=AppointmentStatus.PENDING,
        verbose_name="الحالة",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-time"]

    def __str__(self):
        return f"{self.patient.email} -> {self.doctor.email} ({self.date})"                                                              