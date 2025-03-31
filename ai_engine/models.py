

# ai_engine/models.py
import hashlib
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class AIEngine(models.Model):
    version = models.CharField(max_length=20)
    trained_at = models.DateTimeField(auto_now=True)
    accuracy = models.FloatField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    training_logs = models.TextField(blank=True)
    training_data_hash = models.CharField(max_length=32, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.training_data_hash:
            self.training_data_hash = hashlib.md5(str(self.trained_at).encode()).hexdigest()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"AI Engine v{self.version} ({'Active' if self.is_active else 'Inactive'})"

class RecommendationCache(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    recommendations = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    class Meta:
        indexes = [
            models.Index(fields=['student', 'expires_at']),
        ]