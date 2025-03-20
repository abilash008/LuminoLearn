from django.shortcuts import render

# Create your views here.


# views.py
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, F, Value
from django.db.models.functions import Coalesce

@login_required
def leaderboard(request):
    leaderboard = (
        get_user_model().objects
        .filter(role='student')
        .select_related('profile')
        .annotate(
            total_points=Coalesce(
                Sum('points_earned__points'), 
                Value(0)
            )
        )
        .order_by(F('total_points').desc())
    )
    return render(request, 'student/student_leaderboard.html', {'leaderboard': leaderboard})

