from django.db import models
from django.utils import timezone

from apps.user.models import User
from common import BaseModel


class NotificationType(models.TextChoices):
    ASSIGNMENT_SUBMITTED = "ASSIGNMENT_SUBMITTED", "Assignment submitted"
    ASSIGNMENT_GRADED = "ASSIGNMENT_GRADED", "Assignment graded"
    GENERIC = "GENERIC", "Generic"


class Notification(BaseModel):
    """An in-app notification addressed to a single recipient.

    Created by signals (see signals.py) when a student submits an assignment
    (-> notify the tutor) or when a tutor grades a submission (-> notify the
    student). Generic notifications can also be created manually.
    """

    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    # The user who triggered the notification (student or tutor). Optional so
    # system notifications can omit it. SET_NULL so deleting the actor keeps
    # the recipient's history intact.
    actor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )
    type = models.CharField(
        max_length=32,
        choices=NotificationType.choices,
        default=NotificationType.GENERIC,
    )
    title = models.CharField(max_length=160, blank=True, default="")
    message = models.TextField(blank=True, default="")
    # Frontend route to open when the notification is clicked.
    link = models.CharField(max_length=300, blank=True, default="")
    # Free-form context (submission_id, lesson_id, course_id, grade, ...).
    meta = models.JSONField(default=dict, blank=True)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "notification"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["recipient", "is_read"]),
        ]

    def __str__(self):
        return f"Notification(to={self.recipient_id}, type={self.type})"

    def mark_read(self):
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=["is_read", "read_at", "updated_at"])
