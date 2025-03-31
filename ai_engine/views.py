

# # ai_engine/views.py
# from django.shortcuts import render
# from django.contrib.auth.decorators import login_required
# from django.views.decorators.cache import cache_page
# from .ml_engine import LearningPathRecommender
# from courses.models import Course, StudentAnswer
# from django.db.models import Count, Avg, Case, When, FloatField


# @login_required
# @cache_page(60 * 15)
# def student_recommendations(request):
#     recommender = LearningPathRecommender()
#     recommendations = recommender.recommend_for_student(request.user)
    
#     # Get similar courses based on current enrollments
#     enrolled_courses = request.user.course_enrollments.values_list('course_id', flat=True)
#     similar_courses = Course.objects.exclude(id__in=enrolled_courses).annotate(
#         similar_score=Count('topics', distinct=True)
#     ).order_by('-similar_score')[:5]

#     # Performance data for charts
#     progress_data = {
#     'labels': ['Topic Completion', 'Assignment Score', 'Correct Ratio'],
#     'data': [
#         request.user.course_enrollments.aggregate(
#             Avg('progress__percentage')
#         )['progress__percentage__avg'] or 0,
#         request.user.submissions.aggregate(
#             Avg('answers__is_correct')
#         )['answers__is_correct__avg'] or 0 * 100,
#         StudentAnswer.objects.filter(
#             submission__student=request.user
#         ).aggregate(
#             ratio=Avg(Case(
#                 When(is_correct=True, then=1.0), 
#                 default=0.0
#             ))
#         )['ratio'] or 0 * 100
#     ]
# }

#     return render(request, 'student/student_recommendations.html', {
#         'recommendations': recommendations,
#         'similar_courses': similar_courses,
#         'progress_data': progress_data
#     })