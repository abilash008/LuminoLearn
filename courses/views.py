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

    return render(request, 'create_course.html')

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
    
    return render(request, 'add_topic.html', {'course': course})

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
        assignment = Assignment.objects.create(
            title=title,
            description=description,
            course=course,
            deadline=deadline
        )
        messages.success(request, "Assignment created successfully! Add questions to it.")
        return redirect('add_questions', assignment_id=assignment.id)

    return render(request, 'create_assignment.html', {'course': course})

@login_required
def select_assignment_course(request):
    # Ensure the user is an educator
    if not hasattr(request.user, 'role') or request.user.role != 'educator':
        messages.error(request, "You do not have permission to create assignments.")
        return redirect('home')

    # Get all courses created by this educator
    courses = Course.objects.filter(educator=request.user)
    return render(request, 'select_assignment_course.html', {'courses': courses})


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
    return render(request, 'educator_assignments.html', context)


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

    return render(request, 'add_questions.html', {'assignment': assignment})


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

    return render(request, 'add_choices.html', {'question': question})

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

    return render(request, 'edit_course.html', {'course': course, 'topics':topics })

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

    return render(request, 'delete_course.html', {'course': course})

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
    
    return render(request, 'edit_assignment.html', {
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
    
    return render(request, 'delete_assignment.html', {
        'assignment': assignment
    })
    
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Topic, TopicDiagram

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
    return render(request, 'edit_topic.html', context)


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
    
    return render(request, 'delete_topic.html', {'topic': topic})