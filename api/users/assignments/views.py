"""Student-facing assignment + exercise endpoints.

* POST /api/users/assignment/<lesson_id>/submit/  – upload a submission.
* GET  /api/users/assignment/<lesson_id>/submission/ – fetch own submission.
* POST /api/users/exercise/<lesson_id>/solution/    – reveal exercise solution.

Solution reveal is intentionally a POST so we can later log/quota reveals
without breaking the API contract.
"""

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.course.models.assignment_submission import (
    AssignmentSubmission,
    AssignmentSubmissionFile,
    AssignmentSubmissionStatus,
)
from apps.course.models.lessons import Lessons
from apps.course.models.student_activity import ExerciseSubmission
from common.serializers.courses.assignment_submission import (
    AssignmentSubmissionSerializer,
    AssignmentSubmissionWriteSerializer,
)
from common.serializers.courses.student_activity import ExerciseSubmissionSerializer


def _lesson_visible_to_student(lesson: Lessons, user) -> bool:
    """Student must be enrolled in the lesson's course."""
    return lesson.course_unit.course.enrollments.filter(user=user).exists()


class AssignmentSubmitView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def post(self, request, lesson_id):
        lesson = get_object_or_404(Lessons, pk=lesson_id, kind='ASSIGNMENT')

        if not _lesson_visible_to_student(lesson, request.user):
            return Response(
                {"detail": "You are not enrolled in this course."},
                status=status.HTTP_403_FORBIDDEN,
            )

        note = request.data.get('note', '') or ''

        # Accept one or many files. `files` (multi) takes precedence; fall back
        # to the legacy single `file` key. Only ASSIGNMENT lessons flagged with
        # allow_multiple_files keep more than the first file.
        uploaded = request.FILES.getlist('files') or []
        single = request.FILES.get('file')
        if not uploaded and single:
            uploaded = [single]
        if not lesson.allow_multiple_files:
            uploaded = uploaded[:1]

        if not uploaded and not note.strip():
            return Response(
                {"detail": "Attach at least one file or write a note."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Every submit is a new attempt — earlier attempts are kept as history.
        submission = AssignmentSubmission.objects.create(
            lesson=lesson,
            student=request.user,
            file=uploaded[0] if uploaded else None,
            note=note,
            status=AssignmentSubmissionStatus.SUBMITTED,
        )
        for extra in uploaded[1:]:
            AssignmentSubmissionFile.objects.create(submission=submission, file=extra)

        return Response(
            AssignmentSubmissionSerializer(submission, context={'request': request}).data,
            status=status.HTTP_201_CREATED,
        )


class AssignmentMySubmissionView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, lesson_id):
        """Return the student's full submission history for this lesson.

        Newest first (model Meta ordering). Returns a list so the UI can show
        the latest attempt plus prior graded attempts in one place.
        """
        lesson = get_object_or_404(Lessons, pk=lesson_id, kind='ASSIGNMENT')
        submissions = AssignmentSubmission.objects.filter(
            lesson=lesson, student=request.user
        )
        return Response(
            AssignmentSubmissionSerializer(submissions, many=True, context={'request': request}).data
        )


class ExerciseSolutionView(APIView):
    """Returns the reference solution for an EXERCISE lesson.

    The reference solution is intentionally NOT included in the normal
    student lesson payload (see StudentLessonsSerializer.to_representation)
    so a student can't pull it out of DevTools — they must hit this
    endpoint, which we log/quota in the future.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, lesson_id):
        lesson = get_object_or_404(Lessons, pk=lesson_id, kind='EXERCISE')

        if not _lesson_visible_to_student(lesson, request.user):
            return Response(
                {"detail": "You are not enrolled in this course."},
                status=status.HTTP_403_FORBIDDEN,
            )

        exercise = lesson.exercise or {}
        solution = exercise.get('solution') if isinstance(exercise, dict) else None

        return Response({"solution": solution or ""})


class ExerciseSubmitView(APIView):
    """POST /api/users/exercise/<lesson_id>/submit/ — submit code (upsert)."""

    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def post(self, request, lesson_id):
        lesson = get_object_or_404(Lessons, pk=lesson_id, kind='EXERCISE')
        if not _lesson_visible_to_student(lesson, request.user):
            return Response(
                {"detail": "You are not enrolled in this course."},
                status=status.HTTP_403_FORBIDDEN,
            )

        code = request.data.get('code', '') or ''
        submission, _ = ExerciseSubmission.objects.update_or_create(
            lesson=lesson,
            student=request.user,
            defaults={'code': code},
        )
        return Response(
            ExerciseSubmissionSerializer(submission).data,
            status=status.HTTP_201_CREATED,
        )


class ExerciseMySubmissionView(APIView):
    """GET /api/users/exercise/<lesson_id>/submission/ — the student's own code."""

    permission_classes = [IsAuthenticated]

    def get(self, request, lesson_id):
        lesson = get_object_or_404(Lessons, pk=lesson_id, kind='EXERCISE')
        submission = ExerciseSubmission.objects.filter(
            lesson=lesson, student=request.user
        ).first()
        if not submission:
            return Response({}, status=status.HTTP_204_NO_CONTENT)
        return Response(ExerciseSubmissionSerializer(submission).data)
