from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import (
    CustomUser,
    UserRole,
    PatientProfile,
    DoctorProfile,
    ReceptionistProfile,
)


@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if not created:
        return

    if instance.role == UserRole.PATIENT:
        PatientProfile.objects.create(user=instance)

    elif instance.role == UserRole.DOCTOR:
        DoctorProfile.objects.create(user=instance)

    elif instance.role == UserRole.RECEPTIONIST:
        ReceptionistProfile.objects.create(user=instance)


@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    if instance.role == UserRole.PATIENT and hasattr(instance, "patient_profile"):
        instance.patient_profile.save()

    elif instance.role == UserRole.DOCTOR and hasattr(instance, "doctor_profile"):
        instance.doctor_profile.save()

    elif instance.role == UserRole.RECEPTIONIST and hasattr(
        instance, "receptionist_profile"
    ):
        instance.receptionist_profile.save()
