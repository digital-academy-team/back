# apps/quiz/services/quiz_result.py

from decimal import Decimal

from apps.quiz.models import QuizResult
from apps.course.models.student import CourseStudent, ProgressStatus
from apps.course.models.lessons import Lessons


def submit_quiz(user, quiz, answers):
    total_questions = quiz.questions.count()
    correct_answers = 0
    wrong_answers = 0
    total_score = Decimal("0")

    for answer in answers:
        question = answer["question"]  # already a Question object
        variant = answer["variant"]    # already a Variant object

        if variant.question_id != question.id:
            raise ValueError("Variant does not belong to this question")

        if variant.is_correct:
            correct_answers += 1
            total_score += Decimal(question.points)
        else:
            wrong_answers += 1

    percent = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
    result_status = "PASSED" if percent >= 60 else "FAILED"

    result = QuizResult.objects.create(
        quiz=quiz,
        user=user,
        correct_answers=correct_answers,
        wrong_answers=wrong_answers,
        total_questions=total_questions,
        total=total_score,
        status=result_status,
    )

    course_progress = update_course_progress(user, quiz)
    result.course_progress = course_progress  # attach to result object (not saved to DB)

    return result


def update_course_progress(user, quiz):
    lesson = quiz.lesson
    course = lesson.course_unit.course

    course_student, _ = CourseStudent.objects.get_or_create(user=user, course=course)

    total_lessons = Lessons.objects.filter(course_unit__course=course).count()
    completed_lessons = QuizResult.objects.filter(
        user=user,
        quiz__lesson__course_unit__course=course,
        status="PASSED"
    ).values('quiz__lesson').distinct().count()

    progress = int((completed_lessons / total_lessons) * 100) if total_lessons > 0 else 0

    course_student.progress = progress
    course_student.status = ProgressStatus.COMPLETED if progress == 100 else ProgressStatus.IN_PROGRESS
    course_student.save()

    return progress