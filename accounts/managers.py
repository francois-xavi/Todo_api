from django.contrib.auth.models import BaseUserManager
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    def validate_email(self, email):
        """
        @param email: a string containing the email address
        """
        try:
            validate_email(email)
        except ValidationError:
            raise ValueError(_("Please enter a valid email address."))

    def create_user(self, email, first_name, last_name, password, **extra_fields):
        """
        Create and save a User with the given email
        @param email: a string containing the email address
        @param first_name: a string containing the first name
        @param last_name: a string containing the last name
        @param password: a string containing the password
        @param extra_fields: a dictionary containing extra fields
        @return: a user instance
        """
        if not email:
            raise ValueError(_("Base User Account: An email address is required."))
        self.validate_email(email)
        if not first_name:
            raise ValueError(_("First name is required."))
        if not last_name:
            raise ValueError(_("Last name is required."))

        email = self.normalize_email(email)
        user = self.model(
            email=email, first_name=first_name, last_name=last_name, **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, last_name, password, **extra_fields):
        """
        Create and save a SuperUser with the given email, date of
        @param email: a string containing the email address
        @param first_name: a string containing the first name
        @param last_name: a string containing the last name
        @param password: a string containing the password
        @return: a superuser instance
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_verified", True)

        if not extra_fields.get("is_staff"):
            raise ValueError(_("is_staff must be True for admin user."))
        if not extra_fields.get("is_superuser"):
            raise ValueError(_("is_superuser must be True for admin user."))

        return self.create_user(email, first_name, last_name, password, **extra_fields)
