from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import User, OTPCode

class UserSerializer(serializers.ModelSerializer):
    """User Model Serializer"""
    
    class Meta:
        model = User
        fields = ['id', 'email', 'phone_number', 'first_name', 
                  'last_name', 'is_email_verified', 'date_joined']
        read_only_fields = ['id', 'is_email_verified', 'date_joined', 'email']


class RegisterSerializer(serializers.ModelSerializer):
    """Signup serializer"""
    password = serializers.CharField(write_only=True, required=True, label="Mot de passe", validators=[validate_password], help_text="Enter a password of at least 8 characters.")
    password2 = serializers.CharField(write_only=True, required=True, label="Confirmer le mot de passe", validators=[validate_password], help_text="Enter the same password as above for verification.")

    class Meta:
        model = User
        fields = ['email', 'password', 'password2', 'first_name', 'last_name', 'phone_number']

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Les mots de passe ne correspondent pas."})
        return attrs

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Cet email est déjà utilisé.")
        return value.lower()

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            phone_number=validated_data.get('phone_number', '')
        )
        return user



class LoginSerializer(serializers.Serializer):
    """Login serializer"""
    email = serializers.EmailField(max_length=255, required=True, write_only=True)
    password = serializers.CharField(max_length=68, min_length=6, write_only=True, style={'input_type': 'password'}, required=True)
    access_token = serializers.CharField(max_length=255, read_only=True)
    refresh_token = serializers.CharField(max_length=255, read_only=True)

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("Email ou mot de passe incorrect.")
        user = authenticate(
            request=self.context.get("request"), email=email, password=password
        )
        if not user:
            raise serializers.ValidationError("Email ou mot de passe incorrect.")
        # if not user.is_email_verified:
        #     raise AuthenticationFailed("Email is not verified.")
        tokens = user.tokens()
        return {
            "access_token": str(tokens.get("access")),
            "refresh_token": str(tokens.get("refresh")),
        }

class PasswordResetRequestSerializer(serializers.Serializer):
    """Serializer for password reset request"""
    email = serializers.EmailField(required=True, write_only=True)

    def validate_email(self, value):
        try:
            user = User.objects.get(email=value.lower())
        except User.DoesNotExist:
            raise serializers.ValidationError("Aucun compte avec cet email n'existe.")
        return value.lower()


class PasswordResetVerifySerializer(serializers.Serializer):
    """Serializer for reset password otp verification"""
    email = serializers.EmailField(required=True, write_only=True)
    otp_code = serializers.CharField(required=True, max_length=6, min_length=6, write_only=True)
    new_password = serializers.CharField(write_only=True, required=True, validators=[validate_password], style={'input_type': 'password'})
    new_password2 = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError({"new_password": "Les mots de passe ne correspondent pas."})
        
        email = attrs.get('email').lower()
        otp_code = attrs.get('otp_code')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("Utilisateur non trouvé.")

        # Vérifier l'OTP
        try:
            otp = OTPCode.objects.filter(
                user=user,
                code=otp_code,
                purpose='password_reset',
                is_used=False
            ).latest('created_at')
            
            if not otp.is_valid():
                raise serializers.ValidationError("Le code OTP est expiré ou invalide.")
            
            attrs['user'] = user
            attrs['otp'] = otp
            return attrs
            
        except OTPCode.DoesNotExist:
            raise serializers.ValidationError("Code OTP invalide.")


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for change password (user must be authenticated)"""
    old_password = serializers.CharField(write_only=True, required=True, label="Mot de passe actuel")
    new_password = serializers.CharField(write_only=True, required=True, label="Nouveau mot de passe", validators=[validate_password])
    new_password2 = serializers.CharField(write_only=True, required=True, label="Confirmer le mot de passe")

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError({"new_password": "Les mots de passe ne correspondent pas."})
        return attrs

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Mot de passe actuel incorrect.")
        return value