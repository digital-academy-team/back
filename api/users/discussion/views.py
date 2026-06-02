"""Public discussion posts for DISCUSSION lessons.

* GET  /api/users/discussion/<lesson_id>/posts/  – list every answer (public).
* POST /api/users/discussion/<lesson_id>/posts/  – add your answer.

Visible to anyone enrolled in the course plus the course's tutor. Posts are
public on purpose — this is a comment section, not private notes.
"""

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.course.models.lessons import Lessons
from apps.course.models.student_activity import DiscussionPost
from common.serializers.courses.student_activity import (
    DiscussionPostSerializer,
    DiscussionPostWriteSerializer,
)


def _can_view(lesson: Lessons, user) -> bool:
    course = lesson.course_unit.course
    return course.created_by_id == user.id or course.enrollments.filter(user=user).exists()


class DiscussionPostListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, lesson_id):
        lesson = get_object_or_404(Lessons, pk=lesson_id, kind='DISCUSSION')
        if not _can_view(lesson, request.user):
            return Response(
                {"detail": "You are not enrolled in this course."},
                status=status.HTTP_403_FORBIDDEN,
            )
        posts = DiscussionPost.objects.filter(lesson=lesson).select_related('author')
        return Response(DiscussionPostSerializer(posts, many=True).data)

    def post(self, request, lesson_id):
        lesson = get_object_or_404(Lessons, pk=lesson_id, kind='DISCUSSION')
        if not _can_view(lesson, request.user):
            return Response(
                {"detail": "You are not enrolled in this course."},
                status=status.HTTP_403_FORBIDDEN,
            )
        write = DiscussionPostWriteSerializer(data=request.data)
        write.is_valid(raise_exception=True)
        text = (write.validated_data.get('text') or '').strip()
        if not text:
            return Response({"text": "Write something to post."}, status=status.HTTP_400_BAD_REQUEST)

        post = DiscussionPost.objects.create(lesson=lesson, author=request.user, text=text)
        return Response(DiscussionPostSerializer(post).data, status=status.HTTP_201_CREATED)
