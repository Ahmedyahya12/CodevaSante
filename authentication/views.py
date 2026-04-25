from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import CustomUser, UserRole
from .serializers import (
    PatientRegisterSerializer,
    CustomTokenObtainPairSerializer,
    CurrentUserSerializer,
    FirstLoginSetPasswordSerializer,
    ChangePasswordSerializer,
)


class PatientRegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = PatientRegisterSerializer
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        tags=["Auth"],
        operation_summary="إنشاء حساب مريض",
        request_body=PatientRegisterSerializer,
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response(
            {
                "message": "تم إنشاء حساب المريض بنجاح.",
                "data": CurrentUserSerializer(user).data,
            },
            status=status.HTTP_201_CREATED,
        )


class CustomLoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        tags=["Auth"],
        operation_summary="تسجيل الدخول",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["email", "password"],
            properties={
                "email": openapi.Schema(type=openapi.TYPE_STRING, format="email"),
                "password": openapi.Schema(type=openapi.TYPE_STRING),
            },
        ),
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class CurrentUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        tags=["Auth"],
        operation_summary="بيانات المستخدم الحالي",
        responses={200: CurrentUserSerializer},
    )
    def get(self, request):
        serializer = CurrentUserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class FirstLoginSetPasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        tags=["Auth"],
        operation_summary="تعيين كلمة المرور لأول دخول للطبيب",
        request_body=FirstLoginSetPasswordSerializer,
    )
    def post(self, request):
        user = request.user

        if user.role != UserRole.DOCTOR:
            return Response(
                {"message": "هذه العملية متاحة للطبيب فقط."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if not user.is_first_login:
            return Response(
                {"message": "تم تعيين كلمة المرور مسبقًا لهذا الحساب."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = FirstLoginSetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user.set_password(serializer.validated_data["new_password"])
        user.is_first_login = False
        user.save()

        return Response(
            {"message": "تم تعيين كلمة المرور بنجاح. يمكنك الآن استخدام الحساب بشكل طبيعي."},
            status=status.HTTP_200_OK,
        )


class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        tags=["Auth"],
        operation_summary="تغيير كلمة المرور",
        request_body=ChangePasswordSerializer,
    )
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user

        if not user.check_password(serializer.validated_data["old_password"]):
            return Response(
                {"old_password": "كلمة المرور الحالية غير صحيحة."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(serializer.validated_data["new_password"])
        user.save()

        return Response(
            {"message": "تم تغيير كلمة المرور بنجاح."},
            status=status.HTTP_200_OK,
        )