from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.utils import timezone

class UserManager(BaseUserManager):
    """Define a model manager for User model."""
    use_in_migrations = True

    # Method to save user to the database
    def create_user(self, email, first_name, last_name, password, **extra_fields):
        """
        Creates a User with the given email, first_name, last_name, and password.
        """
        if not email:
            raise ValueError('Invalid Email')
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            first_name=first_name,
            last_name=last_name,
            **extra_fields
        )
        # Call this method for password hashing
        user.set_password(password)
        user.save(using=self._db)
        return user

    # Method called while calling createsuperuser
    def create_superuser(self, email, first_name, last_name, password, **extra_fields):

        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('is_superuser should be True')
        if extra_fields.get('is_staff') is not True:
            raise ValueError('is_staff should be True')

        return self.create_user(email, first_name, last_name, password, **extra_fields) 

class User(AbstractBaseUser, PermissionsMixin):
    # Email field that serves as the username field
    email = models.EmailField( 
        unique=True,
        verbose_name = "Email",
    )
    # need to include is_staff as it's included in django's AdminUser check
    is_staff = models.BooleanField(
        default=False,
        verbose_name = "Is Staff",
    )
    first_name = models.CharField(
        max_length = 20,
        verbose_name = "First Name",
    )
    last_name = models.CharField(
        max_length = 20,
        verbose_name = "Last Name",
    )
    date_joined = models.DateTimeField(
        default=timezone.now
    )
    cellphone = models.CharField(
        max_length=20, 
        null=True,
        blank=True,
        verbose_name = "Cell Phone",
    )
    # is_active = models.BooleanField(default=True)

    USERNAME_FIELD = 'email' # this defines the unique identifier for the User model
    REQUIRED_FIELDS = ['first_name', 'last_name'] # specify any other fields to be require when creating a new user

    objects = UserManager()

    def __str__(self):
        return self.get_full_name()

    def is_staff(self):
        return self.is_staff
    
    def get_full_name(self):
        return self.first_name + ' ' + self.last_name

    def get_first_name(self):
        return self.first_name

    def get_last_name(self):
        return self.last_name

    def get_email(self):
        return self.email

    def get_username(self):
        return self.email
    
    def get_cellphone(self):
        return self.cellphone

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"

        # Simplest possible answer: Yes, always
        return True
