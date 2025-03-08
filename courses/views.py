from decimal import Decimal
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Course, Topic, TopicDiagram, Assignment, Submission, Question, Choice
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
        course = Course.objects.create(
            title=title,
            description=description,
            thumbnail=thumbnail,
            educator=request.user
        )

        messages.success(request, "Course created successfully!")
        return redirect('add_topic', course_id=course.id)

    return render(request, 'courses/create_course.html')

@login_required
def add_topic(request, course_id):
    # Get the course that belongs to the current educator
    course = get_object_or_404(Course, id=course_id, educator=request.user)
    
    if request.method == 'POST':
        topic_name = request.POST.get('topic_name')
        topic_content = request.POST.get('topic_content')
        
        if not topic_name or not topic_content:
            messages.error(request, "Topic name and content are required.")
            return render(request, 'courses/add_topic.html', {'course': course})
        
        # Create the topic
        topic = Topic.objects.create(
            course=course,
            name=topic_name,
            content=topic_content
        )
        
        # Process multiple diagram uploads (if any)
        diagrams = request.FILES.getlist('topic_diagrams')
        for diagram in diagrams:
            TopicDiagram.objects.create(
                topic=topic,
                image=diagram
            )
        
        messages.success(request, "Topic added successfully!")
        # Redirect to educator dashboard or course detail page as needed
        return redirect('educator_dashboard')
    
    return render(request, 'courses/add_topic.html', {'course': course})

@login_required
def manage_courses(request):
    # Ensure the user is an educator
    if not hasattr(request.user, 'role') or request.user.role != 'educator':
        messages.error(request, "You do not have permission to manage courses.")
        return redirect('home')

    # Fetch all courses created by the educator
    courses = Course.objects.filter(educator=request.user)
    return render(request, 'courses/manage_courses.html', {'courses': courses})

@login_required
def review_submissions(request):
    # Ensure the user is an educator
    if not hasattr(request.user, 'role') or request.user.role != 'educator':
        messages.error(request, "You do not have permission to review submissions.")
        return redirect('home')

    # Fetch all submissions for assignments in the educator's courses
    submissions = Submission.objects.filter(assignment__course__educator=request.user)
    return render(request, 'courses/review_submissions.html', {'submissions': submissions})

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
        assignment = Assignment.objects.create(
            title=title,
            description=description,
            course=course,
            deadline=deadline
        )
        messages.success(request, "Assignment created successfully! Add questions to it.")
        return redirect('add_questions', assignment_id=assignment.id)

    return render(request, 'courses/create_assignment.html', {'course': course})

@login_required
def select_assignment_course(request):
    # Ensure the user is an educator
    if not hasattr(request.user, 'role') or request.user.role != 'educator':
        messages.error(request, "You do not have permission to create assignments.")
        return redirect('home')

    # Get all courses created by this educator
    courses = Course.objects.filter(educator=request.user)
    return render(request, 'courses/select_assignment_course.html', {'courses': courses})


@login_required
def educator_assignments(request):
    if not hasattr(request.user, 'role') or request.user.role != 'educator':
        messages.error(request, "Unauthorized access")
        return redirect('home')
    
    # Get assignments through course relationship
    assignments = Assignment.objects.filter(
        course__educator=request.user  # Use double underscore to traverse relationship
    ).select_related('course')
    
    # Get educator's courses
    courses = Course.objects.filter(educator=request.user)
    
    context = {'courses': courses, 'assignments': assignments}
    return render(request, 'courses/educator_assignments.html', context)


@login_required
def add_questions(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id, course__educator=request.user)

    if request.method == 'POST':
        question_text = request.POST.get('question_text')
        question_type = request.POST.get('question_type')
        points = request.POST.get('points')

        question = Question.objects.create(
            assignment=assignment,
            question_text=question_text,
            question_type=question_type,
            points=points
        )

        if question_type == 'multiple_choice':
            return redirect('add_choices', question_id=question.id)

        messages.success(request, "Question added successfully!")
        return redirect('add_questions', assignment_id=assignment.id)

    return render(request, 'courses/add_questions.html', {'assignment': assignment})


@login_required
def add_choices(request, question_id):
    question = get_object_or_404(Question, id=question_id, assignment__course__educator=request.user)

    if request.method == 'POST':
        choice_text = request.POST.get('choice_text')
        is_correct = request.POST.get('is_correct') == 'on'

        Choice.objects.create(
            question=question,
            choice_text=choice_text,
            is_correct=is_correct
        )

        messages.success(request, "Choice added successfully!")
        return redirect('add_choices', question_id=question.id)

    return render(request, 'courses/add_choices.html', {'question': question})

@login_required
def edit_course(request, course_id):
    # Verify educator role and course ownership
    course = get_object_or_404(
        Course, 
        id=course_id,
        educator=request.user
    )
    topics = course.topics.all()

    if request.method == 'POST':
        # Update course details
        course.title = request.POST.get('title', course.title)
        course.description = request.POST.get('description', course.description)
        
        # Handle thumbnail update
        if 'thumbnail' in request.FILES:
            course.thumbnail = request.FILES['thumbnail']
        elif 'thumbnail-clear' in request.POST:
            course.thumbnail = None
        
        course.save()
        messages.success(request, "Course updated successfully!")
        return redirect('manage_courses')

    return render(request, 'courses/edit_course.html', {'course': course, 'topics':topics })

@login_required
def delete_course(request, course_id):
    # Verify educator role and course ownership
    course = get_object_or_404(
        Course, 
        id=course_id,
        educator=request.user
    )

    if request.method == 'POST':
        course.delete()
        messages.success(request, "Course deleted successfully!")
        return redirect('manage_courses')

    return render(request, 'courses/delete_course.html', {'course': course})

@login_required
def edit_assignment(request, assignment_id):
    assignment = get_object_or_404(
        Assignment, 
        id=assignment_id,
        course__educator=request.user
    )
    questions = assignment.questions.all()
    
    if request.method == 'POST':
        # Handle form submission
        assignment.title = request.POST.get('title')
        assignment.description = request.POST.get('description')
        assignment.deadline = request.POST.get('deadline')
        assignment.save()
        
        for question in questions:
            q_text = request.POST.get(f'question_text_{question.id}')
            q_points = request.POST.get(f'question_points_{question.id}')
            if q_text:
                question.question_text = q_text
            if q_points:
                try:
                    question.points = int(q_points)
                except ValueError:
                    question.points = 0
            question.save()
            
            # Loop through choices for each question (if applicable)
            for choice in question.choices.all():
                c_text = request.POST.get(f'choice_text_{choice.id}')
                # Checkbox values come as 'on' if checked
                c_is_correct = request.POST.get(f'is_correct_{choice.id}') == 'on'
                if c_text:
                    choice.choice_text = c_text
                choice.is_correct = c_is_correct
                choice.save()
        
        messages.success(request, "Assignment updated successfully!")
        return redirect('educator_assignments')
    
    return render(request, 'courses/edit_assignment.html', {
        'assignment': assignment,
        'questions': questions,
    })

@login_required
def delete_assignment(request, assignment_id):
    assignment = get_object_or_404(
        Assignment,
        id=assignment_id,
        course__educator=request.user
    )
    
    if request.method == 'POST':
        assignment.delete()
        messages.success(request, "Assignment deleted successfully!")
        return redirect('educator_assignments')
    
    return render(request, 'courses/delete_assignment.html', {
        'assignment': assignment
    })
    
@login_required
def edit_topic(request, topic_id):
    # Get the topic and ensure the logged-in educator owns the course for this topic.
    topic = get_object_or_404(Topic, id=topic_id, course__educator=request.user)
    
    if request.method == 'POST':
        # Update topic fields
        topic.name = request.POST.get('topic_name', topic.name)
        topic.content = request.POST.get('topic_content', topic.content)
        topic.save()
        
        # Optional: Handle diagram updates (if provided)
        # For simplicity, this example does not handle diagram deletion or editing.
        new_diagrams = request.FILES.getlist('topic_diagrams')
        for diagram in new_diagrams:
            TopicDiagram.objects.create(
                topic=topic,
                image=diagram
            )
        
        messages.success(request, "Topic updated successfully!")
        # Redirect back to the edit course page for the topic's course
        return redirect('edit_course', course_id=topic.course.id)
    
    context = {
        'topic': topic,
    }
    return render(request, 'courses/edit_topic.html', context)


@login_required
def delete_topic(request, topic_id):
    # Get topic and verify ownership
    topic = get_object_or_404(
        Topic,
        id=topic_id,
        course__educator=request.user
    )
    
    if request.method == 'POST':
        course_id = topic.course.id
        topic.delete()
        messages.success(request, "Topic deleted successfully!")
        return redirect('edit_course', course_id=course_id)
    
    return render(request, 'courses/delete_topic.html', {'topic': topic})











#    Student Dashboard














from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from courses.models import Course, StudentCourse, Progress, Assignment, Submission
from gamification.models import Gamification
from django.db.models import Avg, Count
from django.contrib import messages
import random
from django.db.models import Q

@login_required
def student_dashboard(request):
    # Ensure the user is a student.
    if not hasattr(request.user, 'role') or request.user.role != 'student':
        messages.error(request, "You do not have permission to view the Student Dashboard.")
        return redirect('home')
    return render(request, 'student_dashboard.html')

# View for Enrolled Courses
@login_required
def student_enrolled_courses(request):
    # Ensure the user is a student.
    if not hasattr(request.user, 'role') or request.user.role != 'student':
        messages.error(request, "You do not have permission to view the Student Dashboard.")
        return redirect('home')
    
    enrollments = StudentCourse.objects.filter(student=request.user)
    enrolled_courses = [enrollment.course for enrollment in enrollments]
    
    return render(request, 'student/student_enrolled_courses.html', {'enrolled_courses': enrolled_courses})


# View for Progress Tracking
# @login_required
# def student_progress(request):
#     if not hasattr(request.user, 'role') or request.user.role != 'student':
#         messages.error(request, "You do not have permission to view the Student Dashboard.")
#         return redirect('home')
    
#     enrollments = StudentCourse.objects.filter(student=request.user)
#     progress_data = []
#     for enrollment in enrollments:
#         # If using a Progress model attached to enrollment; else, set a default.
#         progress = enrollment.progress.percentage if hasattr(enrollment, 'progress') else 0
#         progress_data.append({'course': enrollment.course, 'progress': progress})
    
#     return render(request, 'student/student_progress.html', {'progress_data': progress_data})


@login_required
def student_progress(request):
    if not hasattr(request.user, 'role') or request.user.role != 'student':
        messages.error(request, "You do not have permission to view the Student Dashboard.")
        return redirect('home')
    
    enrollments = StudentCourse.objects.filter(student=request.user)
    progress_data = []
    
    for enrollment in enrollments:
        # Get or create progress record
        progress, created = Progress.objects.get_or_create(
            enrollment=enrollment,
            defaults={'percentage': Decimal('0.00')}
        )
        
        progress_data.append({
            'course': enrollment.course,
            'progress': progress.percentage,
            'completed': progress.completed_topics.count(),
            'total': enrollment.course.topics.count()
        })
    
    return render(request, 'student/student_progress.html', {
        'progress_data': progress_data
    })

# View for Quiz & Assignment Updates
@login_required
def student_assignments(request):
    if not hasattr(request.user, 'role') or request.user.role != 'student':
        messages.error(request, "You do not have permission to view the Student Dashboard.")
        return redirect('home')
    
    enrollments = StudentCourse.objects.filter(student=request.user)
    enrolled_courses = [enrollment.course for enrollment in enrollments]
    upcoming_assignments = Assignment.objects.filter(
        course__in=enrolled_courses
    ).order_by('deadline')
    
    return render(request, 'student/student_assignments.html', {'upcoming_assignments': upcoming_assignments})


# View for Leaderboard & Gamification Stats
@login_required
def student_leaderboard(request):
    if not hasattr(request.user, 'role') or request.user.role != 'student':
        messages.error(request, "You do not have permission to view the Student Dashboard.")
        return redirect('home')
    
    try:
        my_gamification = request.user.gamification
    except Gamification.DoesNotExist:
        my_gamification = None
        
    top_students = Gamification.objects.all().order_by('-points')[:5]
    
    return render(request, 'student/student_leaderboard.html', {
        'my_gamification': my_gamification,
        'top_students': top_students,
    })


# View for Personalized Recommendations
@login_required
def student_recommendations(request):
    if not hasattr(request.user, 'role') or request.user.role != 'student':
        messages.error(request, "You do not have permission to view the Student Dashboard.")
        return redirect('home')
    
    enrollments = StudentCourse.objects.filter(student=request.user)
    enrolled_courses = [enrollment.course for enrollment in enrollments]
    all_courses = list(Course.objects.all())
    recommended_courses = [course for course in all_courses if course not in enrolled_courses]
    if recommended_courses:
        recommended_courses = random.sample(recommended_courses, min(3, len(recommended_courses)))
    else:
        recommended_courses = []
    
    return render(request, 'student/student_recommendations.html', {'recommended_courses': recommended_courses})





@login_required
def search_courses(request):
    # Ensure the user is a student.
    if not hasattr(request.user, 'role') or request.user.role != 'student':
        messages.error(request, "You do not have permission to search courses.")
        return redirect('home')

    query = request.GET.get('q', '')
    results = []
    if query:
        # Filter courses by title or description (case-insensitive)
        results = Course.objects.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )
    
    context = {
        'query': query,
        'results': results,
    }
    return render(request, 'student/student_search_courses.html', context)

@login_required
def enroll_in_course(request, course_id):
    # Enroll the student in the selected course if not already enrolled.
    course = get_object_or_404(Course, id=course_id)
    enrollment, created = StudentCourse.objects.get_or_create(student=request.user, course=course)
    if created:
        messages.success(request, f"You have been enrolled in {course.title}.")
    else:
        messages.info(request, f"You are already enrolled in {course.title}.")
    return redirect('student_enrolled_courses')  # or any page you'd like to redirect to


from django.views.decorators.http import require_GET

@login_required
def course_learn(request, course_id, topic_id=None):
    course = get_object_or_404(Course, id=course_id)
    topics = course.topics.all().order_by('id')
    
    # Ensure active_topic is properly set
    if topic_id:
        active_topic = get_object_or_404(Topic, id=topic_id, course=course)
    else:
        active_topic = topics.first() if topics.exists() else None
    
    context = {
        'course': course,
        'topics': topics,
        'active_topic': active_topic,
    }
    return render(request, 'student/course_learn.html', context)


from django.views.decorators.http import require_POST
from django.db import transaction
import logging
logger = logging.getLogger(__name__)

@require_POST
@login_required
def complete_topic(request, course_id, topic_id):
    try:
        with transaction.atomic():
            # Get course and topic
            course = get_object_or_404(Course, id=course_id)
            topic = get_object_or_404(Topic, id=topic_id, course=course)
            
            # Get or create enrollment and progress
            enrollment, e_created = StudentCourse.objects.get_or_create(
                student=request.user,
                course=course
            )
            progress, p_created = Progress.objects.get_or_create(
                enrollment=enrollment,
                defaults={'percentage': Decimal('0.00')}
            )
            
            # Mark topic as completed if not already
            if not progress.completed_topics.filter(id=topic_id).exists():
                progress.completed_topics.add(topic)
                
                # Update progress using the model method
                progress.update_progress()
            
            # Get next topic only if not the last one
            next_topic = None
            if progress.percentage < 100:
                next_topic = Topic.objects.filter(
                    course=course, 
                    id__gt=topic.id
                ).order_by('id').first()
            
            if next_topic:
                return redirect('course_topic', course_id=course.id, topic_id=next_topic.id)
            else:
                messages.success(request, "Congratulations! You've completed this course!")
                return redirect('course_learn', course_id=course.id)
            
    except Exception as e:
        logger.error(f"Error completing topic: {str(e)}")
        messages.error(request, "Could not update progress. Please try again.")
        return redirect('course_topic', course_id=course_id, topic_id=topic_id)