from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("educator_dashboard/", views.educator_dashboard_view, name="educator_dashboard"),
    path('create_course/', views.create_course, name='create_course'),
    path('manage_courses/', views.manage_courses, name='manage_courses'),
    path('review_submissions/', views.review_submissions, name='review_submissions'),
    path('course/<int:course_id>/create_assignment/', views.create_assignment, name='create_assignment'),
    path('assignment/<int:assignment_id>/add_questions/', views.add_questions, name='add_questions'),
    path('question/<int:question_id>/add_choices/', views.add_choices, name='add_choices'),
    # path('submission/<int:submission_id>/grade/', views.grade_submission, name='grade_submission'),
    path('course/edit/<int:course_id>/', views.edit_course, name='edit_course'),
    path('course/delete/<int:course_id>/', views.delete_course, name='delete_course'),
    path('educator/assignments/', views.educator_assignments, name='educator_assignments'),
    path('assignment/edit/<int:assignment_id>/', views.edit_assignment, name='edit_assignment'),
    path('assignment/delete/<int:assignment_id>/', views.delete_assignment, name='delete_assignment')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)