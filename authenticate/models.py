from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils import timezone
from super_admin.models import Country

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

    
class User(AbstractUser):
    ROLE_CHOICES = (
        (1, 'Super Admin'),
        (2, 'Admin'),
        (3, 'User'),
    )

    username = None
    groups = None
    last_login = None
    date_joined = None
    role_id = models.PositiveSmallIntegerField(choices=ROLE_CHOICES, default=3)
    email = models.EmailField(unique=True)
    is_email_verified = models.BooleanField(default=False)
    date_of_birth = models.DateTimeField(null=True, blank=True)
    gender = models.CharField(max_length=10, null=True, blank=True)
    phone_country_code = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True)
    phone_number = models.CharField(max_length=10, null=True, blank=True)
    profile_picture = models.CharField(max_length=500, null=True, blank=True)
    address_line_one = models.CharField(max_length=100, null=True, blank=True)
    address_line_two = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=50, null=True, blank=True)
    state = models.CharField(max_length=50, null=True, blank=True)
    zip_code = models.CharField(max_length=50, null=True, blank=True)
    country = models.ForeignKey(Country, on_delete=models.DO_NOTHING, related_name='country_user', null=True, blank=True)
    university = models.CharField(max_length=100, null=True, blank=True)
    college = models.CharField(max_length=100, null=True, blank=True)
    created_date = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='created_by_set')
    modified_date = models.DateTimeField(default=timezone.now, null=True, blank=True)
    modified_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='modified_by_set')
    is_active = models.BooleanField(default=True)
    
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

