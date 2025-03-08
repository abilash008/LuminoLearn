from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Topic

@receiver([post_save, post_delete], sender=Topic)
def handle_topic_changes(sender, instance, **kwargs):
    """Update all progress records when topics change"""
    course = instance.course
    for enrollment in course.enrollments.all():
        if hasattr(enrollment, 'progress'):
            enrollment.progress.update_progress()