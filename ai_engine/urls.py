
# ai_engine/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('recommendations/', views.student_recommendations, name='student_recommendations'),
]