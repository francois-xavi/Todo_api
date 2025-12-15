from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import timedelta
import random
import string
from core.services.text_choices_models import OTPType, OTPPurpose
from rest_framework_simplejwt.tokens import RefreshToken
from .managers import UserManager
class User(AbstractUser):
    """
    Custom User model with additional fields
    """
    username = None
    email = models.EmailField(unique=True, verbose_name="Email")
    phone_number = models.CharField(max_length=20, blank=True, null=True, verbose_name="Téléphone")
    is_email_verified = models.BooleanField(default=False)
    is_phone_verified = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = UserManager()

    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"

    def __str__(self):
        return self.email

    def tokens(self):
        token = RefreshToken.for_user(self)
        return {"refresh": str(token), "access": str(token.access_token)}
    
    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        full_name = "%s %s" % (self.first_name or None, self.last_name or None)
        return full_name.strip()

    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name


class OTPCode(models.Model):
    """
    Model for storing OTP codes
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='otp_codes')
    code = models.CharField(max_length=6, verbose_name="Code OTP")
    otp_type = models.CharField(max_length=10, choices=OTPType.choices, default=OTPType.EMAIL)
    purpose = models.CharField(max_length=30, choices=OTPPurpose.choices, default=OTPPurpose.PASSWORD_RESET)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Code OTP"
        verbose_name_plural = "Codes OTP"

    def __str__(self):
        return f"{self.user.email} - {self.code} ({self.purpose})"

    @staticmethod
    def generate_code(length=6):
        """Génère un code OTP aléatoire"""
        return ''.join(random.choices(string.digits, k=length))

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = self.generate_code()
        if not self.expires_at:
            # OTP valide pendant 10 minutes
            self.expires_at = timezone.now() + timedelta(minutes=10)
        super().save(*args, **kwargs)

    def is_valid(self):
        """Vérifie si le code OTP est encore valide"""
        return not self.is_used and timezone.now() < self.expires_at

    def mark_as_used(self):
        """Marque le code comme utilisé"""
        self.is_used = True
        self.save()