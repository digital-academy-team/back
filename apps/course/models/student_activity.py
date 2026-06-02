from django.db import models

from apps.course.models.lessons import Lessons
from apps.user.models import User
from common import BaseModel


class DiscussionPost(BaseModel):
    """A PUBLIC answer to a DISCUSSION lesson prompt.

    Everyone enrolled (plus the course tutor) sees every post, like a comment
    section. Posts are never private.
    """

    lesson = models.ForeignKey(
        Lessons,
        on_delete=models.CASCADE,
        related_name='discussion_posts',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='discussion_posts',
    )
    text = models.TextField()

    class Meta:
        db_table = 'discussion_post'
        ordering = ['created_at']  # chronological, oldest first

    def __str__(self):
        return f"DiscussionPost(lesson={self.lesson_id}, author={self.author_id})"


class ExerciseSubmission(BaseModel):
    """A student's submitted code for an EXERCISE lesson (one current per student)."""

    lesson = models.ForeignKey(
        Lessons,
        on_delete=models.CASCADE,
        related_name='exercise_submissions',
    )
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='exercise_submissions',
    )
    code = models.TextField(blank=True, default='')

    class Meta:
        db_table = 'exercise_submission'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['lesson', 'student'],
                name='uniq_exercise_submission_per_lesson_student',
            ),
        ]

    def __str__(self):
        return f"ExerciseSubmission(lesson={self.lesson_id}, student={self.student_id})"
