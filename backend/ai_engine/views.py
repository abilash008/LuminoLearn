from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response

from backend import courses
from .models import UserPerformance, Recommendation
from .utils import generate_feedback, generate_recommendations

class CourseRecommendationView(APIView):
    def get(self, request, user_id):
        user_performance = UserPerformance.objects.filter(user_id=user_id)
        all_courses = courses.objects.all()
        recommended_ids = generate_recommendations(user_performance, all_courses)
        recommendations = courses.objects.filter(id__in=recommended_ids)
        return Response({"recommendations": [course.title for course in recommendations]})


class AdaptiveFeedbackView(APIView):
    def post(self, request):
        quiz_responses = request.data.get('responses')
        correct_answers = request.data.get('correct_answers')
        feedback = generate_feedback(quiz_responses, correct_answers)
        return Response({"feedback": feedback})
