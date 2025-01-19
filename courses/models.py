

# Create your models here.
from django.db import models
from users.models import CustomUser

class Course(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    educator = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='created_courses', limit_choices_to={'role': 'educator'})
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Assignment(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='assignments')
    deadline = models.DateTimeField()

    def __str__(self):
        return f"{self.title} - {self.course.title}"


class Submission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='submissions', limit_choices_to={'role': 'student'})
    content = models.TextField()
    status = models.CharField(max_length=20, choices=(('pending', 'Pending'), ('graded', 'Graded')), default='pending')
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Submission by {self.student.username} for {self.assignment.title}"
