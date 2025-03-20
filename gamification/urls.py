# gamification/urls.py
from django.urls import path
from . import views

app_name = 'gamification'

urlpatterns = [
    path('leaderboard/', views.leaderboard, name='student_leaderboard'),
]