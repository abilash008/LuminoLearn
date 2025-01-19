

# Create your models here.
from django.db import models
from users.models import CustomUser

class Gamification(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='gamification')
    points = models.IntegerField(default=0)
    badges = models.TextField(blank=True, null=True)  # Store badge details as JSON or comma-separated values

    def __str__(self):
        return f"{self.user.username} - {self.points} points"
