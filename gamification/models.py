

# Create your models here.
# models.py


from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from lumino_learn import settings

class Badge(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='badges/', blank=True, null=True)
    criteria_type = models.CharField(
        max_length=50,
        choices=[
            ('course_completion', 'Course Completion'),
            ('assignment_submission', 'Assignment Submission'),
            ('high_grade', 'High Grade'),
            ('first_submission', 'First Submission'),
            ('points_earned', 'Points Earned'),
        ]
    )
    criteria_threshold = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.name

class UserBadge(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='badges_earned')
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    date_earned = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'badge')

class Point(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='points_earned')
    points = models.IntegerField()
    reason = models.CharField(max_length=255)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True)
    object_id = models.PositiveIntegerField(null=True)
    content_object = GenericForeignKey()
    date_awarded = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        app_label = 'gamification'