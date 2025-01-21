from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

from .managers import CustomUserManager


class User(AbstractBaseUser, PermissionsMixin):
    USER_OPTIONS = [
        ("customer", "customer"),
        ("chef", "chef"),
        ("logistics", "logistics")
    ]
    AUTHENTICATION_PROVIDERS = [
        ("email", "email"),
        ("google", "google"),
        ("facebook", "facebook"),
        ("twitter", "twitter"),
    ]
    email = models.EmailField(_("email address"), unique=True)
    username = models.CharField(_("username"), max_length=20, blank=True, null=False)
    role = models.CharField(choices=USER_OPTIONS, max_length=10, default="customer", verbose_name="Who Am I?")
    provider = models.CharField(choices=AUTHENTICATION_PROVIDERS, default="email", max_length=10)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)

    code = models.IntegerField(blank=True, null=True)
    is_verified = models.BooleanField(default=False)

    # User current Location
    current_location_latitude = models.DecimalField(max_digits=10, decimal_places=10, null=True, blank=True)
    current_location_longitude = models.DecimalField(max_digits=10, decimal_places=10, null=True, blank=True)


    groups = models.ManyToManyField('auth.Group', blank=True, related_name='custom_users+')
    user_permissions = models.ManyToManyField('auth.Permission', blank=True, related_name='custom_users+')


    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    class Meta:
        verbose_name_plural = "Users"
        verbose_name = "User"



    def __str__(self):
        return self.email
    

class UserProfile(models.Model):
    user = models.OneToOneField(User, related_name="profile", on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=30, blank=True, null=True)
    date_of_birth = models.DateField(null=True, blank=True)
    image_url = models.CharField(max_length=1000, blank=True, null=False)
    phone_number = models.CharField(max_length=30, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)

    
    @property
    def get_image_url(self):
        if self.image_url:
            return self.image_url
        else:
            # Change this later when we host images on cloudinary
            return 'https://res.cloudinary.com/daf9tr3lf/image/upload/v1737424631/undraw_profile_male_oovdba_achwuh.png'

    def __str__(self):
        return f"{self.user.email}'s profile"


# User Address
class UserAddress(models.Model):
    LABELLED_PLACES = [
        ("HOME", "HOME"),
        ("WORK", "WORK"),
        ("OTHER", "OTHER"),
    ]
    user = models.ForeignKey(User, related_name="addresses", on_delete=models.CASCADE)
    address = models.TextField(blank=True, null=True)
    street = models.CharField(max_length=100, blank=True, null=False)
    post_code = models.CharField(max_length=30, blank=True, null=False)
    apartment = models.CharField(max_length=50, blank=True, null=False)
    labelled_place = models.CharField(choices=LABELLED_PLACES, max_length=10, blank=False, null=False)

    class Meta:
        verbose_name_plural = "User Addresses"
        verbose_name = "User Address"

    def __str__(self) -> str:
        return self.user.email + " | " + self.address
    

@receiver(post_save, sender=User)
def create_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


@receiver(post_save, sender=User)
def create_token(sender, instance=None, created=False, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)







    