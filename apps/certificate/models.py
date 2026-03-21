from django.db import models

from apps.course.models.course import Course
from apps.user.models import User
from common import BaseModel


class Certificate(BaseModel):

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='certificates')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='certificates')
    certificate = models.FileField(upload_to='certificates')

    def __str__(self):
        return f'{self.course.title} - {self.user.first_name}'


    class Meta:
        db_table = 'certificate'
        unique_together = (('course', 'user'),)
