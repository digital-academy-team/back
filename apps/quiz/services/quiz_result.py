from datetime import timedelta
from decimal import Decimal

from django.db import transaction
from django.db.models import F, Max
from django.utils import timezone

from apps.course.models.lessons import Lessons
from apps.course.models.student import CourseStudent, ProgressStatus
from apps.leaderboard.models import Leaderboard, TierChoice
from apps.quiz.models import QuizResult


def _get_week_range():
    today = timezone.now().date()
    week_start = today - timedelta(days=7)
    week_end = today
    return week_start, week_end


def _resolve_tier(total_stars: int) -> str:
    if total_stars >= 50:
        return TierChoice.PLATINUM
    if total_stars >= 40:
        return TierChoice.GOLD
    if total_stars >= 30:
        return TierChoice.SILVER
    return TierChoice.BRONZE


def upsert_weekly_leaderboard(user):
    week_start, week_end = _get_week_range()

    weekly_results = QuizResult.objects.filter(
        user=user,
        created_at__date__range=[week_start, week_end],
    )

    # Har bir quiz bo'yicha eng yuqori star olinadi.
    per_quiz_max = weekly_results.values("quiz_id").annotate(max_star=Max("stars"))
    total_stars = sum(item["max_star"] or 0 for item in per_quiz_max)

    tier = _resolve_tier(total_stars)

    Leaderboard.objects.update_or_create(
        user=user,
        week_start=week_start,
        week_end=week_end,
        defaults={
            "total_stars": total_stars,
            "tier": tier,
        },
    )

    # Shu hafta bo'yicha positionlarni qayta hisoblaymiz.
    weekly_board = list(
        Leaderboard.objects.filter(
            week_start=week_start,
            week_end=week_end,
        ).order_by("-total_stars", "created_at", "id")
    )

    changed = []
    for idx, row in enumerate(weekly_board, start=1):
        if row.position != idx:
            row.position = idx
            changed.append(row)

    if changed:
        Leaderboard.objects.bulk_update(changed, ["position"])


@transaction.atomic
def submit_quiz(user, quiz, answers):
    total_questions = quiz.questions.count()

    correct_answers = 0
    wrong_answers = 0
    total_score = Decimal("0")

    for answer in answers:
        question = answer["question"]
        variant = answer["variant"]

        if variant.question_id != question.id:
            raise ValueError("Variant does not belong to this question")

        if variant.is_correct:
            correct_answers += 1
            total_score += Decimal(question.points)
        else:
            wrong_answers += 1

    percent = ((correct_answers / total_questions) * 100) if total_questions > 0 else 0

    result_status = "PASSED" if percent >= 60 else "FAILED"

    # STAR CALCULATION
    if 70 <= percent < 80:
        stars = 1
    elif 80 <= percent < 90:
        stars = 2
    elif percent >= 90:
        stars = 3
    else:
        stars = 0

    # ATTEMPT
    attempt = QuizResult.objects.filter(user=user, quiz=quiz).count() + 1

    result = QuizResult.objects.create(
        quiz=quiz,
        user=user,
        correct_answers=correct_answers,
        wrong_answers=wrong_answers,
        total_questions=total_questions,
        total=total_score,
        status=result_status,
        stars=stars,
        attempt=attempt,
    )

    # FIRST ATTEMPT COIN
    if attempt == 1 and percent >= 70:
        last_week_league = (
            Leaderboard.objects.filter(user=user).order_by("-week_end").first()
        )

        coin = 0
        if last_week_league:
            if last_week_league.tier == TierChoice.BRONZE:
                coin = 4
            elif last_week_league.tier == TierChoice.SILVER:
                coin = 6
            elif last_week_league.tier == TierChoice.GOLD:
                coin = 8
            elif last_week_league.tier == TierChoice.PLATINUM:
                coin = 10

        user.coin = F("coin") + coin
        user.save(update_fields=["coin"])

    # COURSE PROGRESS
    course_progress = update_course_progress(user=user, quiz=quiz)
    result.course_progress = course_progress

    # WEEKLY LEADERBOARD CREATE / UPDATE
    upsert_weekly_leaderboard(user=user)

    return result


def update_course_progress(user, quiz):
    lesson = quiz.lesson
    course = lesson.course_unit.course

    course_student, _ = CourseStudent.objects.get_or_create(user=user, course=course)

    total_lessons = Lessons.objects.filter(course_unit__course=course).count()
    completed_lectures = list(course_student.completed_lectures or [])
    lesson_id = str(lesson.id)

    if lesson_id not in completed_lectures:
        completed_lectures.append(lesson_id)

    completed_lessons = Lessons.objects.filter(
        course_unit__course=course,
        id__in=completed_lectures,
    ).count()

    progress = int((completed_lessons / total_lessons) * 100) if total_lessons > 0 else 0

    course_student.completed_lectures = completed_lectures
    course_student.progress = progress
    course_student.status = (
        ProgressStatus.COMPLETED if progress == 100 else ProgressStatus.IN_PROGRESS
    )
    course_student.save()

    return progress
