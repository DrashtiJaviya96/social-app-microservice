from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from rest_framework import generics, mixins, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from drf_spectacular.utils import extend_schema

from .models import UserProfile
from .permissions import IsProfileOwner
from .serializers import (
    UserRegisterSerializer,
    LoginSerializer,
    UserListSerializer,
    UserDetailSerializer,
    UserUpdateSerializer,
    ChangePasswordSerializer,
    ForgotPasswordSerializer,
    ResetPasswordSerializer,
)

@extend_schema(tags=['Health'], summary='Health check')
class HealthView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"status": "ok", "service": "user_service"})

@extend_schema(tags=['Auth'], summary='Register user')
class RegisterView(generics.CreateAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny]

@extend_schema(tags=['Auth'], summary='Login user')
class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

@extend_schema(tags=['Auth'], summary='Logout user')
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return Response(
                    {"detail": "Refresh token is required."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response({"detail": "Logout successful."}, status=status.HTTP_205_RESET_CONTENT)
        except Exception:
            return Response({"detail": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)

@extend_schema(tags=['Users'], summary='List users')
class UserListView(generics.ListAPIView):
    queryset = UserProfile.objects.select_related('user').all().order_by('-created_at')
    serializer_class = UserListSerializer
    permission_classes = [AllowAny]

@extend_schema(tags=['Users'], summary='Retrieve user details')
class UserDetailView(generics.RetrieveAPIView):
    serializer_class = UserDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserProfile.objects.select_related('user').all()

    def get_object(self):
        return get_object_or_404(self.get_queryset(), user__id=self.kwargs['pk'])

@extend_schema(tags=['Users'], summary='Update own profile')
class UserUpdateView(mixins.UpdateModelMixin, generics.GenericAPIView):
    serializer_class = UserUpdateSerializer
    permission_classes = [IsAuthenticated, IsProfileOwner]

    def get_queryset(self):
        return UserProfile.objects.select_related('user').all()

    def get_object(self):
        obj = get_object_or_404(self.get_queryset(), user__id=self.kwargs['pk'])
        self.check_object_permissions(self.request, obj)
        return obj

    def patch(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.partial_update(request, *args, **kwargs)

@extend_schema(tags=['Users'], summary='Delete own profile')
class UserDeleteView(generics.DestroyAPIView):
    serializer_class = UserDetailSerializer
    permission_classes = [IsAuthenticated, IsProfileOwner]

    def get_queryset(self):
        return UserProfile.objects.select_related('user').all()

    def get_object(self):
        obj = get_object_or_404(self.get_queryset(), user__id=self.kwargs['pk'])
        self.check_object_permissions(self.request, obj)
        return obj

    def perform_destroy(self, instance):
        instance.user.delete()

@extend_schema(
    tags=['Auth'],
    summary='Change password',
    request=ChangePasswordSerializer,
    responses={200: {'type': 'object'}}
)
class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user

        if not user.check_password(serializer.validated_data['old_password']):
            return Response(
                {"old_password": "Old password is incorrect."},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.set_password(serializer.validated_data['new_password'])
        user.save()

        return Response({"detail": "Password changed successfully."}, status=status.HTTP_200_OK)

@extend_schema(
    tags=['Auth'],
    summary='Forgot password',
    request=ForgotPasswordSerializer,
    responses={200: {"type": "object"}}
)
class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']

        try:
            user = User.objects.get(email=email)

            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)

            reset_link = f"http://localhost:8080/users/api/v1/reset-password/{uid}/{token}/"

            return Response(
            {
                "detail": "Reset link generated",
                "reset_link": reset_link
            },
            status=status.HTTP_200_OK
)
        except User.DoesNotExist:
            pass

        return Response(
            {"detail": "If an account with that email exists, a reset link has been sent."},
            status=status.HTTP_200_OK
        )

@extend_schema(tags=['Auth'], summary='Reset password')
class ResetPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, uidb64, token):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except Exception:
            return Response({"detail": "Invalid reset link."}, status=status.HTTP_400_BAD_REQUEST)

        if not default_token_generator.check_token(user, token):
            return Response({"detail": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(serializer.validated_data['new_password'])
        user.save()

        return Response({"detail": "Password reset successful."}, status=status.HTTP_200_OK)