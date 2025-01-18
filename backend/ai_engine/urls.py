from django.urls import path
from .views import CourseRecommendationView

urlpatterns = [
    path('recommendations/<int:user_id>/', CourseRecommendationView.as_view(), name='course_recommendations'),
]
