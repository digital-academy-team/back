from django.db import models
from django.db.models import Sum
from django.db.models.enums import TextChoices
from apps.user.models import User
from apps.quiz.models import QuizResult
from common import BaseModel


class TierChoice(TextChoices):
    BRONZE = "BRONZE", "Bronze"
    SILVER = "SILVER", "Silver"
    GOLD = "GOLD", "Gold"
    PLATINUM = "PLATINUM", "Platinum"


class Leaderboard(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    week_start = models.DateField()
    week_end = models.DateField()

    total_stars = models.PositiveIntegerField(default=0)

    tier = models.CharField(
        max_length=20,
        choices=TierChoice.choices,
        default=TierChoice.BRONZE
    )

    position = models.PositiveIntegerField(null=True, blank=True)

    reward_coin = models.PositiveIntegerField(default=0)

    class Meta:
        # unique_together = ("user", "week_start", "week_end")
        ordering = ["position"]