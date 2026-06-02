from django.db import models

from common import BaseModel


class CourseUnit(BaseModel):
    course = models.ForeignKey("Course", on_delete=models.CASCADE, related_name="units")
    title = models.CharField(max_length=120)
    desc = models.TextField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "units"
        ordering = ["order", "created_at"]


    def __str__(self):
        return self.title

