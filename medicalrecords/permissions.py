from rest_framework.permissions import BasePermission
from authentication.models import UserRole
from patients.models import DoctorPatient


class IsDoctor(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == UserRole.DOCTOR


class IsPatient(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == UserRole.PATIENT


class CanAccessMedicalRecord(BasePermission):
    """
    RG-004 & RG-005
    """

    def has_object_permission(self, request, view, obj):
        user = request.user

        # Patient -> فقط سجلاته
        if user.role == UserRole.PATIENT:
            return obj.patient == user

        # Doctor -> فقط مرضاه المرتبطين به
        if user.role == UserRole.DOCTOR:
            return DoctorPatient.objects.filter(
                doctor=user,
                patient=obj.patient,
            ).exists()

        return False