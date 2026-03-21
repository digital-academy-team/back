from django.db import models

from apps.course.models.course import Course
from apps.user.models import User
from common import BaseModel


# Create your models here.


class Comment(BaseModel):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    comment = models.TextField()
    likes = models.PositiveIntegerField(default=0)


    def __str__(self):
        return f"{self.course.title} - {self.user.username}"


    class Meta:
        db_table = 'comments'
        unique_together = (('course', 'user'),)
