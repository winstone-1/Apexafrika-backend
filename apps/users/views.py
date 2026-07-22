
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import (ChangePasswordSerializer, LoginSerializer,
                          PasswordResetConfirmSerializer,
                          PasswordResetSerializer, RegisterSerializer,
                          UserSerializer)

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer


class LoginView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class ProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class UserListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer
    queryset = User.objects.all()
    filterset_fields = ["role", "main_game"]
    search_fields = ["username", "gamer_tag"]


# ==================== PASSWORD RESET ====================


class PasswordResetRequestView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = PasswordResetSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        user = User.objects.filter(email=email).first()

        if user:
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))

            reset_url = f"{
                settings.FRONTEND_URL}/reset-password/{uid}/{token}/"

            subject = "Password Reset - ApexAfrika"
            message = f"""
            Hello {user.username},

            You requested a password reset for your ApexAfrika account.

            Click the link below to reset your password:
            {reset_url}

            If you didn't request this, please ignore this email.

            This link will expire in 24 hours.

            Best,
            The ApexAfrika Team
            """

            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )

        return Response(
            {
                "message": "If an account exists with this email, a password reset link has been sent."
            }
        )


class PasswordResetConfirmView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = PasswordResetConfirmSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        uid = serializer.validated_data["uid"]
        token = serializer.validated_data["token"]
        new_password = serializer.validated_data["new_password"]

        try:
            uid_decoded = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=uid_decoded)
        except (User.DoesNotExist, ValueError, TypeError):
            return Response(
                {"error": "Invalid user"}, status=status.HTTP_400_BAD_REQUEST
            )

        if not default_token_generator.check_token(user, token):
            return Response(
                {"error": "Invalid or expired token"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            validate_password(new_password, user)
        except ValidationError as e:
            return Response(
                {"errors": list(e.messages)}, status=status.HTTP_400_BAD_REQUEST
            )

        user.set_password(new_password)
        user.save()

        return Response(
            {
                "message": "Password reset successful. Please login with your new password."
            }
        )


class ChangePasswordView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ChangePasswordSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        old_password = serializer.validated_data["old_password"]
        new_password = serializer.validated_data["new_password"]

        if not user.check_password(old_password):
            return Response(
                {"error": "Incorrect old password"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            validate_password(new_password, user)
        except ValidationError as e:
            return Response(
                {"errors": list(e.messages)}, status=status.HTTP_400_BAD_REQUEST
            )

        user.set_password(new_password)
        user.save()

        return Response({"message": "Password changed successfully"})


# ==================== GOOGLE OAUTH ====================


@api_view(["POST"])
@permission_classes([permissions.AllowAny])
def google_oauth_login(request):
    """Handle Google OAuth login"""

    code = request.data.get("code")
    redirect_uri = request.data.get("redirect_uri")

    if not code:
        return Response(
            {"error": "Authorization code is required"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        import requests

        token_url = "https://oauth2.googleapis.com/token"
        client_id = settings.SOCIALACCOUNT_PROVIDERS["google"]["APP"]["client_id"]
        client_secret = settings.SOCIALACCOUNT_PROVIDERS["google"]["APP"]["secret"]

        token_data = {
            "code": code,
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
        }

        response = requests.post(token_url, data=token_data)
        token_info = response.json()

        if "access_token" not in token_info:
            return Response(
                {"error": "Failed to get access token"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        userinfo_url = "https://www.googleapis.com/oauth2/v3/userinfo"
        headers = {"Authorization": f"Bearer {token_info['access_token']}"}
        user_response = requests.get(userinfo_url, headers=headers)
        user_info = user_response.json()

        email = user_info.get("email")
        if not email:
            return Response(
                {"error": "Email not provided by Google"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        username = user_info.get("email").split("@")[0]
        if User.objects.filter(username=username).exists():
            username = f"{username}_{User.objects.count()}"

        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                "username": username,
                "gamer_tag": user_info.get("name", username),
            },
        )

        if created:
            user.set_unusable_password()
            user.save()

        from rest_framework_simplejwt.tokens import RefreshToken

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "user": UserSerializer(user).data,
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "is_new_user": created,
            }
        )

    except Exception as e:
        return Response(
            {"error": f"Google OAuth failed: {str(e)}"},
            status=status.HTTP_400_BAD_REQUEST,
        )


# ==================== LOGOUT ====================


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        request.session.flush()
        return Response({"message": "Logged out successfully"})
