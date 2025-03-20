# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from .models import Badge, Point, UserBadge
from courses.models import Submission, Progress

@receiver(post_save, sender=Submission)
def handle_submission_gamification(sender, instance, **kwargs):
    # Award points for on-time submission
    if instance.status == 'submitted' and instance.submitted_at <= instance.assignment.deadline:
        content_type = ContentType.objects.get_for_model(instance)
        if not instance.student.points_earned.filter(content_type=content_type, object_id=instance.id).exists():
            Point.objects.create(
                user=instance.student,
                points=10,
                reason="On-time Submission",
                content_object=instance
            )
    # FIRST SUBMISSION BADGE ONLY
    if Submission.objects.filter(student=instance.student).count() == 1:
        badge, _ = Badge.objects.get_or_create(
            criteria_type='first_submission',
            defaults={
                'name': 'First Assignment',
                'description': 'Awarded for completing your first submission'
            }
        )
        UserBadge.objects.get_or_create(user=instance.student, badge=badge)

@receiver(post_save, sender=Progress)
def handle_course_completion(sender, instance, **kwargs):
    # COURSE COMPLETION BADGE + BONUS POINTS
    if instance.percentage == 100:
        badge, created = Badge.objects.get_or_create(
            criteria_type='course_completion',
            criteria_threshold=instance.enrollment.course.id,
            defaults={
                'name': f'Course Master: {instance.enrollment.course.title}',
                'description': f'Awarded for completing {instance.enrollment.course.title}'
            }
        )
        
        if created or not UserBadge.objects.filter(user=instance.enrollment.student, badge=badge).exists():
            UserBadge.objects.create(user=instance.enrollment.student, badge=badge)
            Point.objects.create(
                user=instance.enrollment.student,
                points=100,
                reason=f"Course Completion: {instance.enrollment.course.title}",
                content_object=instance.enrollment.course
            )