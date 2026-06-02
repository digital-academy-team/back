from django.db import models
from apps.course.models.units import CourseUnit
from common import BaseModel


class Lessons(BaseModel):
    KIND_CHOICES = (
        ('VIDEO', 'Video'),
        ('ARTICLE', 'Reading'),
        ('CHEATSHEET', 'Cheatsheet'),
        ('EXERCISE', 'Exercise'),
        ('QUIZ', 'Quiz'),
        ('ASSIGNMENT', 'Assignment'),
        ('RESOURCE', 'Resource'),
        ('DISCUSSION', 'Discussion'),
    )

    course_unit = models.ForeignKey(CourseUnit, on_delete=models.CASCADE, related_name='lessons')
    kind = models.CharField(max_length=16, choices=KIND_CHOICES, default='VIDEO')
    title = models.CharField(max_length=120)
    desc = models.TextField(blank=True, default='')
    video = models.FileField(upload_to='lessons/video', blank=True, null=True)
    captions = models.FileField(upload_to='lessons/captions', blank=True, null=True)
    presentation = models.FileField(upload_to='lessons/presentation', blank=True, null=True)
    additional_task = models.CharField(max_length=240, blank=True, default='')
    content_md = models.TextField(blank=True, default='')
    duration_min = models.PositiveIntegerField(default=0)
    external_url = models.URLField(blank=True, default='')
    assignment_instructions = models.TextField(blank=True, default='')
    assignment_due_at = models.DateTimeField(blank=True, null=True)
    # ASSIGNMENT: whether a student may attach several files to a submission.
    allow_multiple_files = models.BooleanField(default=False)
    exercise = models.JSONField(blank=True, null=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'lessons'
        ordering = ['order', 'created_at']

    def __str__(self):
        return f"{self.title} - {self.id}"
