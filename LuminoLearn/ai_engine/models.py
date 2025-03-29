'''
# Create your models here.
from django.db import models
from users.models import User
from courses.models import Course

class UserPerformance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    score = models.FloatField()
    completed = models.BooleanField(default=False)
    last_accessed = models.DateTimeField(auto_now=True)

class Recommendation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recommended_course = models.ForeignKey(Course, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

'''