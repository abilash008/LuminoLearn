from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("educator_dashboard/", views.educator_dashboard_view, name="educator_dashboard"),
    path('create_course/', views.create_course, name='create_course'),
    path('course/<int:course_id>/add_topic/', views.add_topic, name='add_topic'),
    path('topic/edit/<int:topic_id>/', views.edit_topic, name='edit_topic'),
    path('topic/delete/<int:topic_id>/', views.delete_topic, name='delete_topic'),
    path('manage_courses/', views.manage_courses, name='manage_courses'),
    path('review_submissions/', views.review_submissions, name='review_submissions'),
    path('assignments/select_course/', views.select_assignment_course, name='select_assignment_course'),
    path('course/<int:course_id>/create_assignment/', views.create_assignment, name='create_assignment'),
    path('assignment/<int:assignment_id>/add_questions/', views.add_questions, name='add_questions'),
    path('question/<int:question_id>/add_choices/', views.add_choices, name='add_choices'),
    path('course/edit/<int:course_id>/', views.edit_course, name='edit_course'),
    path('course/delete/<int:course_id>/', views.delete_course, name='delete_course'),
    path('educator/assignments/', views.educator_assignments, name='educator_assignments'),
    path('assignment/edit/<int:assignment_id>/', views.edit_assignment, name='edit_assignment'),
    path('assignment/delete/<int:assignment_id>/', views.delete_assignment, name='delete_assignment'),
    
    
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('student/enrolled/', views.student_enrolled_courses, name='student_enrolled_courses'),
    path('student/progress/', views.student_progress, name='student_progress'),
    path('student/assignments/', views.student_assignments, name='student_assignments'),
    path('student/leaderboard/', views.student_leaderboard, name='student_leaderboard'),
    path('student/recommendations/', views.student_recommendations, name='student_recommendations'),
    path('student/search_courses/', views.search_courses, name='search_courses'),
    path('student/enroll/<int:course_id>/', views.enroll_in_course, name='enroll_in_course'),
    path('course/<int:course_id>/learn/', views.course_learn, name='course_learn'),
    path('course/<int:course_id>/learn/topic/<int:topic_id>/', views.course_learn, name='course_topic'),
    path('course/<int:course_id>/complete/<int:topic_id>/', views.complete_topic, name='complete_topic'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)