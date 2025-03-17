from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth import get_user_model
import re

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """Create and return a regular user with the given email and password."""
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        extra_fields.setdefault("is_active", True)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and return a superuser with the given email and password."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        # Remove fields that are required for regular users but not superusers
        extra_fields.pop('phone_number', None)
        extra_fields.pop('registration_number', None)
        extra_fields.pop('dob', None)

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    username = None  # Remove username field
    email = models.EmailField(unique=True)  # Primary login field
    phone_number = models.CharField(max_length=15, unique=True, null=True, blank=True)
    registration_number = models.CharField(max_length=20, unique=True, null=True, blank=True)
    dob = models.DateField(null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']  # Remove extra fields for superusers

    objects = CustomUserManager()

    def __str__(self):
        return self.email

User = get_user_model()

# Mapping of roles to role numbers
ROLE_MAPPING = {
    "President": "001",
    "VPE": "002",
    "VPM": "003",
    "VPPR": "004",
    "Treasurer": "005",
    "Secretary": "006",
    "SAA": "007",
}

class Leader(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=50, choices=[(key, key) for key in ROLE_MAPPING.keys()])
    leader_no = models.CharField(max_length=20, unique=True)

    def save(self, *args, **kwargs):
        # Validate leader_no format (must be ROLE_NUMBER/YEAR, e.g., 001/2021)
        pattern = r"^\d{3}/\d{4}$"
        if not re.match(pattern, self.leader_no):
            raise ValueError("Leader number must follow the format ROLE_NUMBER/YEAR (e.g., 001/2021).")

        # Extract role number from leader_no and validate against the role
        try:
            role_number, year = self.leader_no.split('/')
        except ValueError:
            raise ValueError("Leader number format is incorrect. Use ROLE_NUMBER/YEAR (e.g., 001/2021).")

        # Validate role number against the selected role
        expected_role_number = ROLE_MAPPING.get(self.role)
        if expected_role_number is None:
            raise ValueError("Invalid role selected.")

        if role_number != expected_role_number:
            raise ValueError(f"Invalid leader number for the selected role. Expected {expected_role_number}/YEAR.")

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - {self.role} ({self.leader_no})"