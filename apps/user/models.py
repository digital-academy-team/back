from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

from common import BaseModel


class UserRoles(models.TextChoices):
    USER = 'USER', 'user'
    TEACHER = 'TEACHER', 'teachers'
    ADMIN = 'ADMIN', 'admin'
    


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('emial kiritilishi shart.')
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser uchun is_staff=True bo\'lishi kerak.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser uchun is_superuser=True bo\'lishi kerak.')

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser, BaseModel):
    username = models.CharField(max_length=50, unique=True, null=True, blank=True)
    email = models.EmailField(unique=True, null=True, blank=True, db_index=True)
    email_verified = models.BooleanField(default=False)
    email_code = models.CharField(max_length=10, null=True, blank=True)
    email_code_expires_at = models.DateTimeField(null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    phone_number = models.CharField(max_length=20, unique=True, db_index=True, blank=True, null=True)
    phone_code = models.CharField(max_length=10, null=True, blank=True)
    code_expires_at = models.DateTimeField(null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    google_id = models.CharField(max_length=100, unique=True, null=True, blank=True)

    coin = models.PositiveIntegerField(default=0)

    role = models.CharField(max_length=10, choices=UserRoles.choices, default=UserRoles.USER)



    has_real_password = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    class Meta:
        db_table = 'users'

    def __str__(self):
        return self.email or self.username or f"User {self.pk}"


    def set_email_verification_code(self):
        import random
        from datetime import timedelta
        self.email_code = str(random.randint(100000, 999999))
        self.email_code_expires_at = timezone.now() + timedelta(minutes=5)
        self.save(update_fields=['email_code', 'email_code_expires_at'])
