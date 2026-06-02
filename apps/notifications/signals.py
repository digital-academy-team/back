"""Turn assignment submission / grading events into Notification rows.

* Student submits an assignment  -> notify the lesson's tutor.
* Tutor grades a submission       -> notify the student.

All work is wrapped in a broad try/except: a notification failure must never
break the underlying submit / grade request.
"""

import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.course.models.assignment_submission import (
    AssignmentSubmission,
    AssignmentSubmissionStatus,
)

from .models import Notification, NotificationType

logger = logging.getLogger(__name__)


def _display_name(user) -> str:
    if not user:
        return "Someone"
    name = (user.get_full_name() or "").strip()
    return name or user.username or user.email or "Someone"


@receiver(
    post_save,
    sender=AssignmentSubmission,
    dispatch_uid="notifications.on_assignment_submission_saved",
)
def on_assignment_submission_saved(sender, instance: AssignmentSubmission, created, **kwargs):
    try:
        lesson = instance.lesson
        course = lesson.course_unit.course
        tutor = course.created_by
        student = instance.student
        lesson_title = lesson.title

        if instance.status == AssignmentSubmissionStatus.GRADED:
            # The tutor reviewed the work -> tell the student.
            if student is None:
                return
            grade_txt = f" — grade: {instance.grade}" if instance.grade else ""
            Notification.objects.create(
                recipient=student,
                actor=tutor,
                type=NotificationType.ASSIGNMENT_GRADED,
                title="Your submission was graded",
                message=f'Your work for "{lesson_title}" has been reviewed{grade_txt}.',
                link=f"/learn/{course.id}",
                meta={
                    "submission_id": str(instance.id),
                    "lesson_id": str(lesson.id),
                    "course_id": str(course.id),
                    "grade": instance.grade or "",
                },
            )
        else:
            # A new (or re-)submission -> tell the tutor. Skip when the tutor
            # is submitting to their own lesson (e.g. previewing).
            if tutor is None:
                return
            if student is not None and tutor.id == student.id:
                return
            Notification.objects.create(
                recipient=tutor,
                actor=student,
                type=NotificationType.ASSIGNMENT_SUBMITTED,
                title="New assignment submission",
                message=f'{_display_name(student)} submitted "{lesson_title}".',
                link="/instructor?tab=submissions",
                meta={
                    "submission_id": str(instance.id),
                    "lesson_id": str(lesson.id),
                    "course_id": str(course.id),
                },
            )
    except Exception:  # pragma: no cover - defensive: never break the request
        logger.exception("Failed to create notification for submission %s", getattr(instance, "id", None))
