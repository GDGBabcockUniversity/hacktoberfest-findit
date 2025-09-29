from django.db import models
from django.contrib.auth.models import AbstractUser
from .managers import UserProfileManager

# Create your models here.

# Creates Table in db for User Profile
class UserProfile(AbstractUser):
    """User Profile Model"""
    phone_number = models.CharField(max_length=255)
    gender = models.CharField(max_length=10, choices=[('male', 'Male'), ('female', 'Female')], blank=True)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)

    objects = UserProfileManager()
    
    # returns string representation of user
    def __str__(self):
        return f"{self.username} - {self.email}"


# Creates Table in db for Lost Items
class LostItem(models.Model):
    """Lost Item Model"""
    user = models.ForeignKey(UserProfile, on_delete=models.PROTECT)
    description = models.CharField(max_length=255)
    color = models.CharField(max_length=255)
    brand = models.CharField(max_length=255)
    distinctive_features = models.TextField(blank=True)
    time_created = models.DateTimeField(auto_now_add=True)
    last_known_location = models.CharField(max_length=255)
    image = models.ImageField(upload_to='lost_item_images/', blank=True, null=True)

    # returns string representation of lost item
    def __str__(self):
        return f"{self.description} - {self.user.username}"


class FoundItem(models.Model):
    """Found Item Model"""
    user = models.ForeignKey(UserProfile, on_delete=models.PROTECT)
    description = models.CharField(max_length=255)
    color = models.CharField(max_length=255)
    brand = models.CharField(max_length=255)
    distinctive_features = models.TextField(blank=True)
    time_created = models.DateTimeField(auto_now_add=True)
    last_known_location = models.CharField(max_length=255)
    image = models.ImageField(upload_to='found_item_images/', blank=True, null=True)

    # returns string representation of found item
    def __str__(self):
        return f"{self.description} - {self.user.username}"

class Notification(models.Model):
    """Notification Model"""
    to_user = models.ForeignKey(UserProfile, on_delete=models.PROTECT, related_name='to_user')
    from_user = models.ForeignKey(UserProfile, on_delete=models.PROTECT, related_name='from_user')
    message = models.TextField()
    time_created = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)