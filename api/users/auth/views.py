from django.conf import settings
from django.core.mail import send_mail
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from apps.user.services.register import cache_register_data, verify_register_code
from common.serializers.auth.serializer import (
    RegisterSerializer,
    VerifySerializer,
    LoginSerializer,
    UpdatePasswordSerializer,
)


class AuthViewSet(viewsets.GenericViewSet):
    permission_classes = [AllowAny]

    def get_permissions(self):
        if self.action == "update_password":
            return [IsAuthenticated()]
        return [AllowAny()]

    def get_serializer_class(self):
        if self.action == "register":
            return RegisterSerializer
        elif self.action == "verify_code":
            return VerifySerializer
        elif self.action == "update_password":
            return UpdatePasswordSerializer
        return LoginSerializer

    @action(
        detail=False,
        methods=["post"],
        url_path="register",
        permission_classes=[AllowAny],
    )
    def register(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data["username"]
        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]

        code = cache_register_data(
            username=username,
            email=email,
            password=password,
        )

        send_mail(
            subject="Your verification code",
            message=f"Your verification code is: {code}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )

        return Response(
            {
                "message": "Verification code sent successfully.",
            },
            status=status.HTTP_200_OK,
        )

    @action(
        detail=False,
        methods=["post"],
        url_path="verify-code",
        permission_classes=[AllowAny],
    )
    def verify_code(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        code = serializer.validated_data["code"]

        user, error = verify_register_code(email=email, code=code)

        if error:
            return Response(
                {"detail": error},
                status=status.HTTP_400_BAD_REQUEST,
            )

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "message": "User registered successfully.",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                },
                "tokens": {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
            },
            status=status.HTTP_201_CREATED,
        )

    @action(
        detail=False,
        methods=["post"],
        url_path="login",
        permission_classes=[AllowAny],
    )
    def login(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "message": "Login successful.",
                "requires_password_change": getattr(user, "is_temporary_password", False),
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "role": user.role,
                },
                "tokens": {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
            },
            status=status.HTTP_200_OK,
        )

    @action(
        detail=False,
        methods=["post"],
        url_path="update-password",
        permission_classes=[IsAuthenticated],
    )
    def update_password(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save(user=request.user)
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "message": "Password updated successfully.",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                },
                "tokens": {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
            },
            status=status.HTTP_200_OK,
        )