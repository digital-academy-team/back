from django.db import models

from apps.quiz.models.quiz import Quiz
from common import BaseModel


class Questions(BaseModel):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    points = models.IntegerField(default=0)

    class Meta:
        db_table = 'questions'

    def __str__(self):
        return self.question_text
