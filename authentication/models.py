from django.db import models
from django.contrib.auth.models import AbstractUser
from .managers import CustomUserManager


class UserRole(models.TextChoices):
    PATIENT = "patient", "مريض"
    DOCTOR = "doctor", "طبيب"
    RECEPTIONIST = "receptionist", "موظف استقبال"
    ADMIN = "admin", "مدير"


class CustomUser(AbstractUser):
    username = None

    email = models.EmailField(unique=True, verbose_name="البريد الإلكتروني")
    first_name = models.CharField(max_length=150, verbose_name="الاسم الأول")
    last_name = models.CharField(max_length=150, verbose_name="اسم العائلة")
    phone = models.CharField(max_length=20, blank=True, verbose_name="رقم الهاتف")
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.PATIENT,
        verbose_name="الدور",
    )
    is_first_login = models.BooleanField(default=False, verbose_name="أول تسجيل دخول")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="آخر تحديث")

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    objects = CustomUserManager()

    class Meta:
        verbose_name = "مستخدم"
        verbose_name_plural = "المستخدمون"
        ordering = ["-created_at"]

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()


class PatientProfile(models.Model):
    GENDER_CHOICES = [
        ("M", "ذكر"),
        ("F", "أنثى"),
    ]

    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="patient_profile",
        verbose_name="المستخدم",
    )
    date_of_birth = models.DateField(
        null=True, blank=True, verbose_name="تاريخ الميلاد"
    )
    gender = models.CharField(
        max_length=1, choices=GENDER_CHOICES, blank=True, verbose_name="الجنس"
    )
    address = models.TextField(blank=True, verbose_name="العنوان")
    national_id = models.CharField(
        max_length=30, blank=True, verbose_name="الرقم الوطني"
    )
    emergency_contact = models.CharField(
        max_length=100, blank=True, verbose_name="جهة اتصال للطوارئ"
    )
    medical_notes = models.TextField(blank=True, verbose_name="ملاحظات طبية")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "ملف المريض"
        verbose_name_plural = "ملفات المرضى"

    def __str__(self):
        return f"ملف المريض: {self.user.full_name or self.user.email}"


class DoctorProfile(models.Model):
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="doctor_profile",
        verbose_name="المستخدم",
    )
    specialty = models.CharField(max_length=150, blank=True, verbose_name="التخصص")
    bio = models.TextField(blank=True, verbose_name="نبذة")
    years_of_experience = models.PositiveIntegerField(
        default=0, verbose_name="سنوات الخبرة"
    )
    available = models.BooleanField(default=True, verbose_name="متاح")

    class Meta:
        verbose_name = "ملف الطبيب"
        verbose_name_plural = "ملفات الأطباء"

    def __str__(self):
        return f"ملف الطبيب: {self.user.full_name or self.user.email}"


class ReceptionistProfile(models.Model):
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="receptionist_profile",
        verbose_name="المستخدم",
    )
    active = models.BooleanField(default=True, verbose_name="نشط")
    notes = models.TextField(blank=True, verbose_name="ملاحظات")

    class Meta:
        verbose_name = "ملف موظف الاستقبال"
        verbose_name_plural = "ملفات موظفي الاستقبال"

    def __str__(self):
        return f"ملف الاستقبال: {self.user.full_name or self.user.email}"
