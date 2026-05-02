from django.db import models
from authentication.models import DoctorProfile


class DoctorWorkingHour(models.Model):
    DAYS = [
        (0, "الإثنين"),
        (1, "الثلاثاء"),
        (2, "الأربعاء"),
        (3, "الخميس"),
        (4, "الجمعة"),
        (5, "السبت"),
        (6, "الأحد"),
    ]

    doctor = models.ForeignKey(
        DoctorProfile,
        on_delete=models.CASCADE,
        related_name="working_hours",
        verbose_name="الطبيب",
    )
    day_of_week = models.IntegerField(choices=DAYS, verbose_name="اليوم")
    start_time = models.TimeField(verbose_name="بداية العمل")
    end_time = models.TimeField(verbose_name="نهاية العمل")
    max_patients_per_slot = models.PositiveIntegerField(default=1, verbose_name="عدد المرضى في نفس الوقت")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["day_of_week", "start_time"]
        unique_together = ("doctor", "day_of_week", "start_time", "end_time")

    def __str__(self):
        return f"{self.doctor.user.full_name} - {self.get_day_of_week_display()} {self.start_time}-{self.end_time}"
