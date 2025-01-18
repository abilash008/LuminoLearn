'''

from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def generate_recommendations(user_performance, all_courses):
    # Example: Collaborative filtering (simplified)
    user_scores = np.array([perf.score for perf in user_performance])
    course_matrix = np.array([course.vector for course in all_courses])  # Assume course vector exists
    recommendations = cosine_similarity(user_scores.reshape(1, -1), course_matrix)
    return recommendations.argsort()[-5:]  # Top 5 recommendations


def generate_feedback(quiz_responses, correct_answers):
    feedback = []
    for i, (response, correct) in enumerate(zip(quiz_responses, correct_answers)):
        if response != correct:
            feedback.append(f"Question {i+1}: Review topic '{correct.topic}'.")
    return feedback


'''