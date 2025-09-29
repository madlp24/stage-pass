from django.db import models
from django.contrib.auth import get_user_model

# Create your models here.

User = get_user_model()

class UserProfile(models.Model):
    ROLE_CHOICES = [("USER","User"),("ORGANIZER","Organizer"),("ADMIN","Admin")]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(max_length=12, choices=ROLE_CHOICES, default="USER")

    def __str__(self):
        return f"{self.user.username} ({self.role})"
