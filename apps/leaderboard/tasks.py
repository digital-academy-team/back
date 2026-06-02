from collections import defaultdict
from django.db.models import Max, F
from django.utils import timezone
from celery import shared_task

from apps.quiz.models import QuizResult
from apps.leaderboard.models import Leaderboard
from apps.user.models import User


@shared_task
def calculate_weekly_league():

    today = timezone.now().date()

    week_start = today - timezone.timedelta(days=7)
    week_end = today

    results = QuizResult.objects.filter(
        created_at__date__range=[week_start, week_end]
    )

    user_stars = defaultdict(int)

    users = User.objects.all()

    for user in users:

        quizzes = (
            results.filter(user=user)
            .values("quiz")
            .annotate(max_star=Max("stars"))
        )

        total = sum(item["max_star"] for item in quizzes)

        user_stars[user.id] = total

    ranking = sorted(
        user_stars.items(),
        key=lambda x: x[1],
        reverse=True
    )

    top_rewards = {
        1: 50,
        2: 40,
        3: 30,
        4: 20,
        5: 10,
    }

    for index, (user_id, total_stars) in enumerate(ranking, start=1):

        if total_stars >= 50:
            tier = "PLATINUM"
            weekly_coin = 10

        elif total_stars >= 40:
            tier = "GOLD"
            weekly_coin = 8

        elif total_stars >= 30:
            tier = "SILVER"
            weekly_coin = 6

        elif total_stars >= 20:
            tier = "BRONZE"
            weekly_coin = 4

        else:
            tier = "BRONZE"
            weekly_coin = 0

        reward = weekly_coin

        if index in top_rewards:
            reward += top_rewards[index]

        Leaderboard.objects.create(
            user_id=user_id,
            week_start=week_start,
            week_end=week_end,
            total_stars=total_stars,
            tier=tier,
            position=index,
            reward_coin=reward,
        )

        User.objects.filter(id=user_id).update(
            coin=F("coin") + reward
        )