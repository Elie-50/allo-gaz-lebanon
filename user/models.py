from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator

phone_number_validator = RegexValidator(
    regex=r'^\+[1-9]\d{6,14}$',
    message='Enter a valid international phone number in E.164 format (e.g., +12345678901).'
)

# Create your models here.
class User(AbstractUser):
    middle_name = models.CharField(max_length=50, blank=True, null=True, default="")
    phone_number = models.CharField(
        max_length=20, 
        blank=True, 
        null=False, 
        validators=[phone_number_validator],
        default=''
    )

    is_driver = models.BooleanField(default=False, db_index=True)
    region = models.CharField(max_length=100, null=False, blank=True, default='')