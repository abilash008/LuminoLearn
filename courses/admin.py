

# Register your models here.
from django.contrib import admin
from .models import Course, Assignment, Submission

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'educator', 'created_at')
    search_fields = ('title', 'educator__username')
    list_filter = ('created_at',)

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'deadline')
    search_fields = ('title', 'course__title')

@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('assignment', 'student', 'status', 'submitted_at')
    list_filter = ('status', 'submitted_at')
    search_fields = ('assignment__title', 'student__username')
