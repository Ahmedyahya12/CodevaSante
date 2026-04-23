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
        operation_description="يمكن للمريض إنشاء حساب جديد في النظام.",
        request_body=PatientRegisterSerializer,
        responses={
            201: openapi.Response(
                description="تم إنشاء حساب المريض بنجاح.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "message": openapi.Schema(type=openapi.TYPE_STRING),
                        "data": openapi.Schema(type=openapi.TYPE_OBJECT),
                    },
                ),
            ),
            400: "بيانات غير صالحة",
        },
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        response_serializer = self.get_serializer(user)

        return Response(
            {
                "message": "تم إنشاء حساب المريض بنجاح.",
                "data": response_serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )


class CustomLoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        tags=["Auth"],
        operation_summary="تسجيل الدخول",
        operation_description="تسجيل الدخول باستخدام البريد الإلكتروني وكلمة المرور.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["email", "password"],
            properties={
                "email": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format=openapi.FORMAT_EMAIL,
                    description="البريد الإلكتروني",
                    example="admin@gmail.com",
                ),
                "password": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="كلمة المرور",
                    example="Admin@12345",
                ),
            },
        ),
        responses={
            200: openapi.Response(
                description="تم تسجيل الدخول بنجاح",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "refresh": openapi.Schema(type=openapi.TYPE_STRING),
                        "access": openapi.Schema(type=openapi.TYPE_STRING),
                        "user": openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                                "email": openapi.Schema(type=openapi.TYPE_STRING),
                                "first_name": openapi.Schema(type=openapi.TYPE_STRING),
                                "last_name": openapi.Schema(type=openapi.TYPE_STRING),
                                "full_name": openapi.Schema(type=openapi.TYPE_STRING),
                                "phone": openapi.Schema(type=openapi.TYPE_STRING),
                                "role": openapi.Schema(type=openapi.TYPE_STRING),
                                "role_display": openapi.Schema(type=openapi.TYPE_STRING),
                                "is_first_login": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                            },
                        ),
                    },
                ),
            ),
            401: "بيانات الدخول غير صحيحة",
        },
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class CurrentUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        tags=["Auth"],
        operation_summary="بيانات المستخدم الحالي",
        operation_description="إرجاع بيانات المستخدم المسجل دخوله حاليًا.",
        responses={
            200: CurrentUserSerializer,
            401: "غير مصرح",
        },
    )
    def get(self, request):
        serializer = CurrentUserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class FirstLoginSetPasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        tags=["Auth"],
        operation_summary="تعيين كلمة المرور لأول دخول للطبيب",
        operation_description="يستعمل هذا endpoint فقط للطبيب عند أول تسجيل دخول.",
        request_body=FirstLoginSetPasswordSerializer,
        responses={
            200: openapi.Response(description="تم تعيين كلمة المرور بنجاح."),
            400: "طلب غير صالح",
            403: "غير مسموح",
        },
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
            {
                "message": "تم تعيين كلمة المرور بنجاح. يمكنك الآن استخدام الحساب بشكل طبيعي."
            },
            status=status.HTTP_200_OK,
        )


class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        tags=["Auth"],
        operation_summary="تغيير كلمة المرور",
        operation_description="يمكن للمستخدم المسجل دخوله تغيير كلمة المرور الحالية.",
        request_body=ChangePasswordSerializer,
        responses={
            200: openapi.Response(description="تم تغيير كلمة المرور بنجاح."),
            400: "بيانات غير صالحة",
            401: "غير مصرح",
        },
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
