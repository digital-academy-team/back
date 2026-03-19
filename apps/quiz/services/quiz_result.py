from decimal import Decimal

from apps.course.models.student import CourseStudent
from apps.quiz.models import QuizResult


def submit_quiz(user, quiz, answers):
    total_questions = quiz.questions.count()
    correct_answers = 0
    wrong_answers = 0
    total_score = Decimal("0")

    for answer in answers:
        question = answer["question"]
        selected_variant = answer["variant"]

        if selected_variant.is_correct:
            correct_answers += 1
            total_score += question.points
        else:
            wrong_answers += 1

    percent = 0
    if total_questions > 0:
        percent = (correct_answers / total_questions) * 100

    status = "PASSED" if percent >= 60 else "FAILED"

    result = QuizResult.objects.create(
        quiz=quiz,
        user=user,
        correct_answers=correct_answers,
        wrong_answers=wrong_answers,
        total_questions=total_questions,
        total=total_score,
        status=status,
    )

    return result