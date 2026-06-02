from django.db import models

from apps.course.models.lessons import Lessons
from apps.user.models import User
from common import BaseModel


class AssignmentSubmissionStatus(models.TextChoices):
    SUBMITTED = "SUBMITTED", "Submitted"
    GRADED = "GRADED", "Graded"


class AssignmentSubmission(BaseModel):
    """A student-uploaded artifact for an ASSIGNMENT-kind Lesson."""

    lesson = models.ForeignKey(
        Lessons,
        on_delete=models.CASCADE,
        related_name='assignment_submissions',
    )
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='assignment_submissions',
    )
    file = models.FileField(upload_to='assignments/submissions/', blank=True, null=True)
    note = models.TextField(blank=True, default='')
    grade = models.CharField(max_length=10, blank=True, default='')
    feedback = models.TextField(blank=True, default='')
    status = models.CharField(
        choices=AssignmentSubmissionStatus.choices,
        default=AssignmentSubmissionStatus.SUBMITTED,
        max_length=16,
    )

    class Meta:
        db_table = 'assignment_submission'
        # No unique (lesson, student) constraint: a student can submit multiple
        # times and every attempt is kept as history. The newest row (by
        # created_at) is the "current" submission.
        ordering = ['-created_at']

    def __str__(self):
        return f"AssignmentSubmission(lesson={self.lesson_id}, student={self.student_id})"


class AssignmentSubmissionFile(BaseModel):
    """An extra file attached to a submission (beyond the primary ``file``).

    Lets a student upload several files in one attempt when the lesson has
    ``allow_multiple_files=True``.
    """

    submission = models.ForeignKey(
        AssignmentSubmission,
        on_delete=models.CASCADE,
        related_name='files',
    )
    file = models.FileField(upload_to='assignments/submissions/')

    class Meta:
        db_table = 'assignment_submission_file'
        ordering = ['created_at']
