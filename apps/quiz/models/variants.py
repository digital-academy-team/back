from django.db import models

from apps.quiz.models.questions import Questions
from common import BaseModel


class Variant(BaseModel):
    question = models.ForeignKey(Questions, on_delete=models.CASCADE, related_name='variants')
    text = models.TextField()
    is_correct = models.BooleanField()


    class Meta:
        db_table = 'variants'


    def __str__(self):
        return self.text
