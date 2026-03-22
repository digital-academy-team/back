from django.db import models

from apps.course.models.course import Course
from apps.user.models import User
from common import BaseModel


# Create your models here.

class ProgressStatus(models.TextChoices):
    COMPLETED = "COMPLETED", "Completed"
    IN_PROGRESS = "IN_PROGRESS", "In Progress"


class CourseStudent(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='students')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='students')
    progress = models.PositiveIntegerField(default=0)
    status = models.CharField(choices=ProgressStatus.choices, default=ProgressStatus.IN_PROGRESS, max_length=20)
    certificate_pdf = models.FileField(upload_to='certificates/', null=True, blank=True)

    class Meta:
        db_table = 'course_student'


    def __str__(self):
        return f"{self.id}"

