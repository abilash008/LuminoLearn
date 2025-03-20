# courses/templatetags/assignment_tags.py
from django import template
from courses.models import StudentAnswer

register = template.Library()

@register.filter
def get_question_answer(answers, question):
    try:
        return answers.filter(question=question).first()
    except AttributeError:
        return None