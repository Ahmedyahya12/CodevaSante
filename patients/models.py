from django.conf import settings
from django.db import models


class DoctorPatient(models.Model):
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="doctor_patients",
        verbose_name="الطبيب",
    )
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="patient_doctors",
        verbose_name="المريض",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الربط")

    class Meta:
        verbose_name = "ربط طبيب بمريض"
        verbose_name_plural = "روابط الأطباء والمرضى"
        unique_together = ("doctor", "patient")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.doctor.email} -> {self.patient.email}"