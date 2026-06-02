from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.course.models.assignment_submission import (
    AssignmentSubmission,
    AssignmentSubmissionStatus,
)
from apps.course.models.lessons import Lessons
from common.serializers.courses.assignment_submission import (
    AssignmentSubmissionGradeSerializer,
    AssignmentSubmissionSerializer,
)


def _lesson_owned_by(teacher, lesson) -> bool:
    return lesson.course_unit.course.created_by_id == teacher.id


class TutorSubmissionInboxView(APIView):
    """GET /api/teachers/assignment/submissions/

    Every submission across all ASSIGNMENT lessons in courses the requesting
    tutor created. Powers the dashboard "Submissions" inbox so a tutor can
    review and grade student work in one place instead of digging into each
    lesson. Optional ?status=SUBMITTED|GRADED filter.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        submissions = (
            AssignmentSubmission.objects.filter(
                lesson__course_unit__course__created_by=request.user
            )
            .select_related(
                'student',
                'lesson',
                'lesson__course_unit',
                'lesson__course_unit__course',
            )
        )

        status_filter = request.query_params.get('status')
        if status_filter in AssignmentSubmissionStatus.values:
            submissions = submissions.filter(status=status_filter)

        return Response(AssignmentSubmissionSerializer(submissions, many=True, context={'request': request}).data)


class AssignmentSubmissionListView(APIView):
    """GET /api/teachers/assignment/<lesson_id>/submissions/"""

    permission_classes = [IsAuthenticated]

    def get(self, request, lesson_id):
        lesson = get_object_or_404(Lessons, pk=lesson_id, kind='ASSIGNMENT')

        if not _lesson_owned_by(request.user, lesson):
            return Response(
                {"detail": "Only the lesson's tutor can view submissions."},
                status=status.HTTP_403_FORBIDDEN,
            )

        submissions = AssignmentSubmission.objects.filter(lesson=lesson).select_related('student')
        return Response(AssignmentSubmissionSerializer(submissions, many=True, context={'request': request}).data)


class AssignmentSubmissionGradeView(APIView):
    """PATCH /api/teachers/assignment/submission/<submission_id>/grade/"""

    permission_classes = [IsAuthenticated]

    def patch(self, request, submission_id):
        submission = get_object_or_404(AssignmentSubmission, pk=submission_id)

        if not _lesson_owned_by(request.user, submission.lesson):
            return Response(
                {"detail": "Only the lesson's tutor can grade submissions."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = AssignmentSubmissionGradeSerializer(submission, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(status=AssignmentSubmissionStatus.GRADED)

        return Response(AssignmentSubmissionSerializer(submission, context={'request': request}).data)
