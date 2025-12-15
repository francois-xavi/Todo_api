from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import action as action_decorator
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg.utils import swagger_auto_schema
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.conf import settings
from core.services.text_choices_models import OTPType, OTPPurpose

from .models import User, OTPCode
from .serializers import (
    RegisterSerializer, LoginSerializer, UserSerializer,
    PasswordResetRequestSerializer, PasswordResetVerifySerializer,
    ChangePasswordSerializer
)
from core.utils.utils import send_otp_email


def get_tokens_for_user(user):
    """Generate JWT tokens for a user"""
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class AuthViewSet(viewsets.GenericViewSet):
    """
    ViewSet for all authentication operations
    
    Available actions:
    - register: User registration
    - login: User login
    - logout: User logout
    - me: Get user profile
    - update_me: Update user profile
    - change_password: Change password
    - reset_password: Request password reset (OTP)
    - verify_reset: Verify OTP and reset password
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    def get_permissions(self):
        """Dynamic permissions based on action"""
        if self.action in ['register', 'login', 'reset_password', 'verify_reset']:
            self.permission_classes = [permissions.AllowAny]
        else:
            self.permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in self.permission_classes]
    
    def get_serializer_class(self):
        """Dynamic serializer based on action"""
        if self.action == 'register':
            return RegisterSerializer
        elif self.action == 'login':
            return LoginSerializer
        elif self.action == 'change_password':
            return ChangePasswordSerializer
        elif self.action == 'reset_password':
            return PasswordResetRequestSerializer
        elif self.action == 'verify_reset':
            return PasswordResetVerifySerializer
        return UserSerializer
    
    @swagger_auto_schema(
        operation_description="Register a new user",
        operation_summary="Register",
        responses={201: UserSerializer}
    )
    @action_decorator(
        detail=False,
        methods=['post'],
        url_path='register',
        permission_classes=[permissions.AllowAny]
    )
    def register(self, request):
        """
        POST /api/auth/register/
        {
            "username": "john_doe",
            "email": "john@example.com",
            "password": "SecurePass123!",
            "password2": "SecurePass123!",
            "first_name": "John",
            "last_name": "Doe"
        }
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @swagger_auto_schema(
        operation_description="Login a user",
        operation_summary="Login",
    )
    @action_decorator(
        detail=False,
        methods=["post"],
        url_path="login",
        permission_classes=[permissions.AllowAny],
    )
    def login(self, request):
        serializer = LoginSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    # @swagger_auto_schema(
    #     operation_description="Logout user (blacklist refresh token)",
    #     operation_summary="Logout"
    # )
    # @action_decorator(
    #     detail=False,
    #     methods=['post'],
    #     url_path='logout',
    #     permission_classes=[permissions.IsAuthenticated]
    # )
    # def logout(self, request):
    #     """
    #     POST /api/auth/logout/
    #     {
    #         "refresh": "refresh_token_here"
    #     }
    #     """
    #     try:
    #         refresh_token = request.data.get("refresh")
    #         token = RefreshToken(refresh_token)
    #         token.blacklist()
    #         return Response({
    #             'message': 'Logout successful'
    #         }, status=status.HTTP_200_OK)
    #     except Exception as e:
    #         return Response({
    #             'error': 'Invalid token'
    #         }, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(
        operation_description="Get authenticated user profile",
        operation_summary="Get profile"
    )
    @action_decorator(
        detail=False,
        methods=['get'],
        url_path='me',
        permission_classes=[permissions.IsAuthenticated]
    )
    @method_decorator(never_cache)
    def me(self, request):
        """
        GET /api/auth/me/
        """
        serializer = UserSerializer(request.user, context={'request': request})
        return Response(serializer.data)
    
    @swagger_auto_schema(
        operation_description="Update authenticated user profile",
        operation_summary="Update profile", 
        responses={200: UserSerializer}
    )
    @action_decorator(
        detail=False,
        methods=['patch'],
        url_path='update-me',
        permission_classes=[permissions.IsAuthenticated]
    )
    @method_decorator(never_cache)
    def update_me(self, request):
        """
        PATCH /api/auth/update-me/
        {
            "first_name": "John",
            "last_name": "Doe Updated",
            "phone_number": "+229123456789"
        }
        """
        instance = request.user
        serializer = UserSerializer(
            instance,
            data=request.data,
            partial=True,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    
    @swagger_auto_schema(
        operation_description="Change password for authenticated user",
        operation_summary="Change password"
    )
    @action_decorator(
        detail=False,
        methods=['post'],
        url_path='change-password',
        permission_classes=[permissions.IsAuthenticated]
    )
    def change_password(self, request):
        """
        POST /api/auth/change-password/
        {
            "old_password": "OldPass123!",
            "new_password": "NewPass123!",
            "new_password2": "NewPass123!"
        }
        """
        serializer = self.get_serializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        return Response({
            'message': 'Password changed successfully'
        }, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        operation_description="Request password reset (sends OTP via email)",
        operation_summary="Request password reset"
    )
    @action_decorator(
        detail=False,
        methods=['post'],
        url_path='reset-password',
        permission_classes=[permissions.AllowAny]
    )
    def reset_password(self, request):
        """
        POST /api/auth/reset-password/
        {
            "email": "john@example.com"
        }
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        user = User.objects.get(email=email)
        
        # Invalidate old unused OTPs
        OTPCode.objects.filter(
            user=user,
            purpose=OTPPurpose.PASSWORD_RESET,
            is_used=False
        ).update(is_used=True)
        
        # Create new OTP code
        otp_code = OTPCode.objects.create(
            user=user,
            otp_type=OTPType.EMAIL,
            purpose=OTPPurpose.PASSWORD_RESET
        )
        
        # Send OTP via email
        email_sent = send_otp_email(user, otp_code)
        
        if email_sent:
            return Response({
                'message': 'Un code de verification vous a été envoyé par mail',
                'email': email
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'error': 'Une erreur est survenue lors de l\'envoi du code de verification'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @swagger_auto_schema(
        operation_description="Verify OTP and reset password",
        operation_summary="Verify OTP and reset password"
    )
    @action_decorator(
        detail=False,
        methods=['post'],
        url_path='verify-reset',
        permission_classes=[permissions.AllowAny]
    )
    def verify_reset(self, request):
        """
        POST /api/auth/verify-reset/
        {
            "email": "john@example.com",
            "otp_code": "123456",
            "new_password": "NewSecurePass123!",
            "new_password2": "NewSecurePass123!"
        }
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']
        otp = serializer.validated_data['otp']
        new_password = serializer.validated_data['new_password']
        
        # Change password
        user.set_password(new_password)
        user.save()
        
        # Mark OTP as used
        otp.mark_as_used()
        
        return Response({
            'message': 'Password reset successfully'
        }, status=status.HTTP_200_OK)