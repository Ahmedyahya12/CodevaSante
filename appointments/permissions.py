
from rest_framework.permissions import BasePermission
from authentication.models import UserRole


class IsPatient(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == UserRole.PATIENT


class IsReceptionist(BasePermission):
    def has_permission(self, request, view):
        return request.user.role in [UserRole.RECEPTIONIST, UserRole.ADMIN]


class IsDoctor(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == UserRole.DOCTOR

from rest_framework.permissions import BasePermission


class IsDoctor(BasePermission):
    message = "هذه الصلاحية مخصصة للطبيب فقط."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == "doctor"
        )
