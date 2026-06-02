from django.db.models.enums import TextChoices
from django.db import models

from .quiz import Quiz
from apps.user.models import User
from common import BaseModel


class QuizResultStatus(TextChoices):
    PASSED = "PASSED", "Passed"
    FAILED = "FAILED", "Failed"


class QuizResult(BaseModel):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="results")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="quiz_results")
    correct_answers = models.PositiveIntegerField(default=0)
    wrong_answers = models.PositiveIntegerField(default=0)
    total_questions = models.PositiveIntegerField(default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(
        max_length=10,
        choices=QuizResultStatus.choices,
        default=QuizResultStatus.FAILED,
    )

    stars = models.PositiveIntegerField(default=0)
    attempt = models.PositiveIntegerField(default=1)

    class Meta:
        db_table = "quiz_result"

    def __str__(self):
        return f"{self.quiz} | {self.user}"