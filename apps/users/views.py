from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django_otp import devices_for_user
from django_otp.plugins.otp_totp.models import TOTPDevice
import qrcode
import base64
from io import BytesIO
from .serializers import (
    UserSerializer, RegisterSerializer, LoginSerializer,
    PasswordResetSerializer, PasswordResetConfirmSerializer,
    ChangePasswordSerializer, TwoFASetupSerializer, TwoFAVerifySerializer
)

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
    filterset_fields = ['role', 'main_game']
    search_fields = ['username', 'gamer_tag']

# ==================== PASSWORD RESET ====================

class PasswordResetRequestView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = PasswordResetSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        user = User.objects.filter(email=email).first()
        
        if user:
            # Generate token and send email
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            reset_url = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}/"
            
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
                fail_silently=False
            )
        
        # Always return success to prevent email enumeration
        return Response({
            'message': 'If an account exists with this email, a password reset link has been sent.'
        })

class PasswordResetConfirmView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = PasswordResetConfirmSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        uid = serializer.validated_data['uid']
        token = serializer.validated_data['token']
        new_password = serializer.validated_data['new_password']
        
        try:
            uid_decoded = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=uid_decoded)
        except (User.DoesNotExist, ValueError, TypeError):
            return Response(
                {'error': 'Invalid user'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not default_token_generator.check_token(user, token):
            return Response(
                {'error': 'Invalid or expired token'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate password
        try:
            validate_password(new_password, user)
        except ValidationError as e:
            return Response(
                {'errors': list(e.messages)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.set_password(new_password)
        user.save()
        
        return Response({
            'message': 'Password reset successful. Please login with your new password.'
        })

class ChangePasswordView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ChangePasswordSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        old_password = serializer.validated_data['old_password']
        new_password = serializer.validated_data['new_password']
        
        if not user.check_password(old_password):
            return Response(
                {'error': 'Incorrect old password'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            validate_password(new_password, user)
        except ValidationError as e:
            return Response(
                {'errors': list(e.messages)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.set_password(new_password)
        user.save()
        
        return Response({
            'message': 'Password changed successfully'
        })

# ==================== GOOGLE OAUTH ====================

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def google_oauth_login(request):
    """Handle Google OAuth login"""
    from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
    from allauth.socialaccount.providers.oauth2.client import OAuth2Client
    from django.http import JsonResponse
    
    code = request.data.get('code')
    redirect_uri = request.data.get('redirect_uri')
    
    if not code:
        return Response(
            {'error': 'Authorization code is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Exchange code for access token
        import requests
        token_url = 'https://oauth2.googleapis.com/token'
        client_id = settings.SOCIALACCOUNT_PROVIDERS['google']['APP']['client_id']
        client_secret = settings.SOCIALACCOUNT_PROVIDERS['google']['APP']['secret']
        
        token_data = {
            'code': code,
            'client_id': client_id,
            'client_secret': client_secret,
            'redirect_uri': redirect_uri,
            'grant_type': 'authorization_code'
        }
        
        response = requests.post(token_url, data=token_data)
        token_info = response.json()
        
        if 'access_token' not in token_info:
            return Response(
                {'error': 'Failed to get access token'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get user info
        userinfo_url = 'https://www.googleapis.com/oauth2/v3/userinfo'
        headers = {'Authorization': f"Bearer {token_info['access_token']}"}
        user_response = requests.get(userinfo_url, headers=headers)
        user_info = user_response.json()
        
        # Create or get user
        email = user_info.get('email')
        if not email:
            return Response(
                {'error': 'Email not provided by Google'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        username = user_info.get('email').split('@')[0]
        # Ensure unique username
        if User.objects.filter(username=username).exists():
            username = f"{username}_{User.objects.count()}"
        
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'username': username,
                'gamer_tag': user_info.get('name', username),
                'avatar': user_info.get('picture', None)
            }
        )
        
        if created:
            user.set_unusable_password()
            user.save()
        
        # Generate JWT tokens
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'is_new_user': created
        })
        
    except Exception as e:
        return Response(
            {'error': f'Google OAuth failed: {str(e)}'},
            status=status.HTTP_400_BAD_REQUEST
        )

# ==================== TWO-FACTOR AUTH (2FA) ====================

class TwoFASetupView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TwoFASetupSerializer

    def get(self, request):
        """Get 2FA setup QR code"""
        user = request.user
        
        # Check if 2FA already enabled
        if user.is_2fa_enabled:
            return Response({
                'message': '2FA already enabled',
                'is_enabled': True
            })
        
        # Create TOTP device
        device = TOTPDevice.objects.create(
            user=user,
            name='default',
            confirmed=False
        )
        
        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(device.config_url)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        qr_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
        
        return Response({
            'device_id': device.id,
            'secret': device.key,
            'qr_code': f"data:image/png;base64,{qr_base64}",
            'is_enabled': False
        })

    def post(self, request):
        """Verify and enable 2FA"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        device_id = serializer.validated_data['device_id']
        code = serializer.validated_data['code']
        
        try:
            device = TOTPDevice.objects.get(id=device_id, user=request.user, confirmed=False)
        except TOTPDevice.DoesNotExist:
            return Response(
                {'error': 'Invalid device'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if device.verify_token(code):
            device.confirmed = True
            device.save()
            
            # Enable 2FA for user
            user = request.user
            user.is_2fa_enabled = True
            user.totp_device = device
            user.save()
            
            # Generate backup codes
            import secrets
            backup_codes = []
            for i in range(10):
                backup_codes.append(secrets.token_hex(4))
            user.backup_codes = backup_codes
            user.save()
            
            return Response({
                'message': '2FA enabled successfully',
                'backup_codes': backup_codes,
                'is_enabled': True
            })
        else:
            return Response(
                {'error': 'Invalid verification code'},
                status=status.HTTP_400_BAD_REQUEST
            )

class TwoFAVerifyView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TwoFAVerifySerializer

    def post(self, request):
        """Verify 2FA code during login"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        code = serializer.validated_data['code']
        remember_device = serializer.validated_data.get('remember_device', False)
        
        # Check if 2FA is enabled
        if not user.is_2fa_enabled:
            return Response(
                {'error': '2FA is not enabled for this user'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verify TOTP
        if user.totp_device and user.totp_device.verify_token(code):
            # Store 2FA verification in session
            request.session['2fa_verified'] = True
            if remember_device:
                request.session['2fa_remember'] = True
            
            return Response({
                'message': '2FA verification successful',
                'verified': True
            })
        
        # Check backup codes
        if code in user.backup_codes:
            # Remove used backup code
            user.backup_codes.remove(code)
            user.save()
            
            request.session['2fa_verified'] = True
            if remember_device:
                request.session['2fa_remember'] = True
            
            return Response({
                'message': '2FA verification successful (backup code)',
                'verified': True,
                'backup_code_used': True
            })
        
        return Response(
            {'error': 'Invalid verification code'},
            status=status.HTTP_400_BAD_REQUEST
        )

class TwoFADisableView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        """Disable 2FA"""
        user = request.user
        
        if not user.is_2fa_enabled:
            return Response(
                {'error': '2FA is not enabled'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.disable_2fa()
        
        return Response({
            'message': '2FA disabled successfully',
            'is_enabled': False
        })

class TwoFAStatusView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Get 2FA status"""
        user = request.user
        
        return Response({
            'is_enabled': user.is_2fa_enabled,
            'has_backup_codes': len(user.backup_codes) > 0,
            'backup_codes_count': len(user.backup_codes)
        })

# ==================== LOGOUT ====================

class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        # Clear session
        request.session.flush()
        return Response({
            'message': 'Logged out successfully'
        })
