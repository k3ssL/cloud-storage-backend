from django.contrib.auth import get_user_model
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator, RegexValidator
from django.db import models
from rest_framework.authtoken.models import Token


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, **extra_fields)
class User(AbstractBaseUser):
    username = None
    last_login = None
    email = models.EmailField(max_length=254, unique=True)
    password = models.CharField(
        max_length=256,
        validators=[
            MinLengthValidator(3, message='Пароль слишком короткий'),
            RegexValidator(
                regex=r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)',
                message='Пароль должен содержать одну строчную букву, одну заглавную и одну цифру'
            )
        # RegexValidator используется для применения регулярного выражения,
        # которое проверяет наличие хотя бы одной строчной буквы ((?=.*[a-z])),
        # хотя бы одной заглавной буквы ((?=.*[A-Z]))
        # и хотя бы одной цифры ((?=.*\d)).
        ],
    )
    first_name = models.CharField(max_length=254)
    last_name = models.CharField(max_length=254)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []


