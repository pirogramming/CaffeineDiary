from django.db import models
from django.conf import settings

# Create your models here.
class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    body_weight_kg = models.FloatField(null=True, blank=True)      
    target_sleeptime = models.TimeField(null=True, blank=True)         
    profile_image = models.ImageField(upload_to="profile_images/", null=True, blank=True) 

    def __str__(self):
        return f"{self.user.username} UserProfile"