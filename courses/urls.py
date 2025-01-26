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
    path('submission/<int:submission_id>/grade/', views.grade_submission, name='grade_submission'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)