import pytest
from accounts.models import User, OTPCode, OTPPurpose, OTPType


@pytest.fixture
def user_data():
    """Données valides pour créer un utilisateur"""
    return {
        'email': 'newuser@example.com',
        'password': 'SecurePass123!',
        'password2': 'SecurePass123!',
        'first_name': 'John',
        'last_name': 'Doe',
        'phone_number': '+229123456789'
    }


@pytest.fixture
def another_user(db):
    """Second utilisateur pour tests"""
    return User.objects.create_user(
        email='another@example.com',
        password='TestPass123!',
        first_name='Another',
        last_name='User'
    )


@pytest.fixture
def otp_code(user):
    """OTP valide pour reset password"""
    otp = OTPCode.objects.create(
        user=user,
        otp_type=OTPType.EMAIL,
        purpose=OTPPurpose.PASSWORD_RESET
    )
    return otp


@pytest.fixture
def expired_otp(user):
    """OTP expiré"""
    from django.utils import timezone
    from datetime import timedelta
    
    past_time = timezone.now() - timedelta(minutes=15)
    return OTPCode.objects.create(
        user=user,
        otp_type=OTPType.EMAIL,
        purpose=OTPPurpose.PASSWORD_RESET,
        expires_at=past_time
    )