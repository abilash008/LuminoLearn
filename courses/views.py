from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Course, Assignment, Submission
from django.utils.timezone import now

@login_required
def educator_dashboard_view(request):
    # Ensure the user is an educator
    if not hasattr(request.user, 'role') or request.user.role != 'educator':
        messages.error(request, "You do not have permission to access the Educator Dashboard.")
        return redirect('home')

    # Fetch courses created by the educator
    courses = Course.objects.filter(educator=request.user)
    submissions = Submission.objects.filter(assignment__course__educator=request.user, status='pending')
    return render(request, 'educator_dashboard.html', {'courses': courses,'submissions': submissions,})

@login_required
def create_course(request):
    # Ensure the user is an educator
    if not hasattr(request.user, 'role') or request.user.role != 'educator':
        messages.error(request, "You do not have permission to create courses.")
        return redirect('home')

    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        thumbnail = request.FILES.get('thumbnail')

        # Create a new course
        Course.objects.create(
            title=title,
            description=description,
            thumbnail=thumbnail,
            educator=request.user
        )
        messages.success(request, "Course created successfully!")
        return redirect('educator_dashboard')

    return render(request, 'create_course.html')

@login_required
def manage_courses(request):
    # Ensure the user is an educator
    if not hasattr(request.user, 'role') or request.user.role != 'educator':
        messages.error(request, "You do not have permission to manage courses.")
        return redirect('home')

    # Fetch all courses created by the educator
    courses = Course.objects.filter(educator=request.user)
    return render(request, 'manage_courses.html', {'courses': courses})

@login_required
def review_submissions(request):
    # Ensure the user is an educator
    if not hasattr(request.user, 'role') or request.user.role != 'educator':
        messages.error(request, "You do not have permission to review submissions.")
        return redirect('home')

    # Fetch all submissions for assignments in the educator's courses
    submissions = Submission.objects.filter(assignment__course__educator=request.user)
    return render(request, 'review_submissions.html', {'submissions': submissions})

@login_required
def create_assignment(request, course_id):
    # Ensure the user is an educator
    if not hasattr(request.user, 'role') or request.user.role != 'educator':
        messages.error(request, "You do not have permission to create assignments.")
        return redirect('home')

    course = get_object_or_404(Course, id=course_id, educator=request.user)

    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        deadline = request.POST.get('deadline')

        # Validate and create the assignment
        Assignment.objects.create(
            title=title,
            description=description,
            course=course,
            deadline=deadline
        )
        messages.success(request, "Assignment created successfully!")
        return redirect('manage_courses')

    return render(request, 'create_assignment.html', {'course': course})

@login_required
def grade_submission(request, submission_id):
    # Ensure the user is an educator
    if not hasattr(request.user, 'role') or request.user.role != 'educator':
        messages.error(request, "You do not have permission to grade submissions.")
        return redirect('home')

    submission = get_object_or_404(Submission, id=submission_id, assignment__course__educator=request.user)

    if request.method == 'POST':
        grade = request.POST.get('grade')
        submission.grade = grade
        submission.status = 'graded'
        submission.save()
        messages.success(request, "Submission graded successfully!")
        return redirect('review_submissions')

    return render(request, 'grade_submission.html', {'submission': submission})


