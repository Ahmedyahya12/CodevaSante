from django.db import models

# Create your models here. 
from django.conf import settings
from django.db import models


class MedicalRecord(models.Model):
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="medical_records",
        verbose_name="المريض",
    )
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="doctor_records",
        verbose_name="الطبيب",
    )
    note = models.TextField(verbose_name="ملاحظة طبية")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.patient.email} - {self.doctor.email}"
