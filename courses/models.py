

# Create your models here.
from django.db import models
from django.conf import settings
from django.utils import timezone

class Course(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    thumbnail = models.ImageField(upload_to='course_thumbnails/', null=True, blank=True)
    educator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_courses', limit_choices_to={'role': 'educator'})
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class Topic(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='topics')
    name = models.CharField(max_length=255)
    content = models.TextField()

    def __str__(self):
        return self.name

class TopicDiagram(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='diagrams')
    image = models.ImageField(upload_to='topic_diagrams/')

    def __str__(self):
        return f"Diagram for {self.topic.name}"

class Assignment(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    course = models.ForeignKey('Course', on_delete=models.CASCADE, related_name='assignments')
    deadline = models.DateTimeField()
    # created_at = models.DateTimeField(default=timezone.now)
    # updated_at = models.DateTimeField(auto_now=True)
    # created_at = models.DateTimeField(auto_now_add=True)  # Automatically set on creation
    # updated_at = models.DateTimeField(auto_now=True)      # Automatically updated on save

    def __str__(self):
        return f"{self.title} - {self.course.title}"


class Submission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='submissions', limit_choices_to={'role': 'student'})
    status = models.CharField(max_length=20, choices=(('pending', 'Pending'), ('graded', 'Graded')), default='pending')
    submitted_at = models.DateTimeField(auto_now_add=True)
    grade = models.CharField(max_length=10, null=True, blank=True)

    def __str__(self):
        return f"Submission by {self.student.username} for {self.assignment.title}"


class Question(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    question_type = models.CharField(
        max_length=20,
        choices=[('short_answer', 'Short Answer'), ('multiple_choice', 'Multiple Choice'), ('code', 'Code-Based')],
    )
    points = models.IntegerField(default=0)

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    choice_text = models.CharField(max_length=200)
    is_correct = models.BooleanField(default=False)
    
    
    
#  Student Dashboard



class StudentCourse(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='enrollments',
        limit_choices_to={'role': 'student'}
    )
    course = models.ForeignKey(
        'Course', 
        on_delete=models.CASCADE,
        related_name='enrollments'
    )
    enrolled_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username} enrolled in {self.course.title}"


class Progress(models.Model):
    enrollment = models.OneToOneField(StudentCourse, on_delete=models.CASCADE, related_name='progress')
    # For simplicity, we store progress as a percentage
    percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.enrollment.student.username}: {self.percentage}% in {self.enrollment.course.title}"



