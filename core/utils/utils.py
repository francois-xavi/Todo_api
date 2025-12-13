import os
import uuid
from django.core.mail import send_mail
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
# import requests
import logging
import random
import string


logger = logging.getLogger(__name__)



def generate_unique_code(length, prefix=None, digit_only=False):
    """
    :param length:  positive int
    :param prefix: string
    :param digit_only: bool
    :return: string
    """
    if length <= 0:
        raise ValueError("Length must be a positive integer.")

    if digit_only:
        code = "".join(random.choice(string.digits) for _ in range(length))
    else:
        characters = '0123456789abcdef'
        code = "".join(random.choice(characters) for _ in range(length))
    if prefix:
        code = prefix + code
    return code


def generate_hex_id(length):
    return uuid.uuid4().hex[:length]

def generate_hex_id_4():
    """Generate a random UUID."""
    return uuid.uuid4().hex[:4]

def generate_hex_id_6():
    """Generate a random UUID."""
    return uuid.uuid4().hex[:6]

def send_otp_email(user, otp_code):
    """Envoie l'OTP par email"""
    subject = 'Code de réinitialisation de mot de passe'
    message = f"""
    Bonjour {user.get_full_name()},
    
    Votre code de réinitialisation de mot de passe est : {otp_code.code}
    
    Ce code est valide pendant 10 minutes.
    
    Si vous n'avez pas demandé cette réinitialisation, ignorez ce message.
    
    Cordialement,
    L'équipe TODO API
    """
    
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Erreur d'envoi email: {e}")
        return False