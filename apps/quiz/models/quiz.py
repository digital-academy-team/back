from apps.course.models.lessons import Lessons
from apps.user.models import User
from common import BaseModel
from django.db import models

class Quiz(BaseModel):
    lesson = models.ForeignKey(Lessons, on_delete=models.CASCADE, related_name='quizzes')
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quizzes')
    title = models.CharField(max_length=100)
    description = models.TextField()
    time_limit_min = models.PositiveIntegerField(default=0)
    show_timer = models.BooleanField(default=True)
    is_finished = models.BooleanField(default=False)
    due_at = models.DateTimeField(blank=True, null=True)


    class Meta:
        db_table = 'quiz'

    def __str__(self):
        return self.title
