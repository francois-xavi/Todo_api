from django.db import models
from django.utils.translation import gettext_lazy as _


class OTPType(models.TextChoices):
    EMAIL = 'email', _('Email')
    SMS = 'sms', _('SMS')


class OTPPurpose(models.TextChoices):
    PASSWORD_RESET = 'password_reset', _('Password Reset')
    EMAIL_VERIFICATION = 'email_verification', _('Email Verification')
    PHONE_VERIFICATION = 'phone_verification', _('Phone Verification')