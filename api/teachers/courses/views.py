import traceback

from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.course.models.course import Course
from apps.course.models.lessons import Lessons
from apps.course.models.units import CourseUnit
from common.permission import IsCourseTeacherOrAdmin
from common.serializers.courses.course import CourseCreateSerializer, CourseUpdateSerializer, CourseDetailSerializer
from common.serializers.courses.units import CourseUnitListSerializer


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    http_method_names = ["get", "post", "patch", "delete"]
    permission_classes = [IsAuthenticated, IsCourseTeacherOrAdmin]
    parser_classes = [FormParser, JSONParser, MultiPartParser]


    def get_serializer_class(self):
        if self.action == 'create':
            return CourseCreateSerializer

        if self.action in ['update', 'partial_update']:
            return CourseUpdateSerializer

        return CourseDetailSerializer


    def get_queryset(self):
        return super().get_queryset().filter(created_by=self.request.user)


    def create(self, request, *args, **kwargs):
        try:

            serializer = self.get_serializer(
                data=request.data,
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)

            self.perform_create(serializer)

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            print("ERROR:", str(e))
            print(traceback.format_exc())

            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=["post"], url_path="units")
    def create_unit(self, request, pk=None):
        course = self.get_object()
        title = str(request.data.get("title") or "").strip()
        desc = str(request.data.get("desc") or "").strip()

        if not title:
            return Response(
                {"title": "Unit title is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        next_order = course.units.count()
        unit = CourseUnit.objects.create(course=course, title=title, desc=desc, order=next_order)
        return Response(CourseUnitListSerializer(unit).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["patch"], url_path=r"units/(?P<unit_id>[^/.]+)")
    def update_unit(self, request, pk=None, unit_id=None):
        """PATCH /api/teachers/courses/<id>/units/<unit_id>/ — edit title/desc."""
        course = self.get_object()
        unit = get_object_or_404(CourseUnit, pk=unit_id, course=course)

        if "title" in request.data:
            title = str(request.data.get("title") or "").strip()
            if not title:
                return Response(
                    {"title": "Unit title cannot be empty."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            unit.title = title
        if "desc" in request.data:
            unit.desc = str(request.data.get("desc") or "")
        unit.save()

        return Response(CourseUnitListSerializer(unit).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="reorder")
    def reorder(self, request, pk=None):
        """Persist a drag-and-drop reorder of units and lessons.

        Body: {"units": [{"id": <unit_id>, "lessons": [<lesson_id>, ...]}, ...]}

        Units are renumbered by their position in the list; lessons by their
        position within each unit's `lessons` array. A lesson listed under a
        different unit than it currently belongs to is re-parented (cross-unit
        drag). Everything is validated against this course so a tutor can't
        move another course's lessons.
        """
        course = self.get_object()  # enforces object permission (owner/admin)
        units_payload = request.data.get("units")
        if not isinstance(units_payload, list):
            return Response({"units": "Expected a list."}, status=status.HTTP_400_BAD_REQUEST)

        valid_unit_ids = set(map(str, course.units.values_list("id", flat=True)))
        valid_lesson_ids = set(
            map(str, Lessons.objects.filter(course_unit__course=course).values_list("id", flat=True))
        )

        with transaction.atomic():
            for unit_index, unit_entry in enumerate(units_payload):
                unit_id = str(unit_entry.get("id"))
                if unit_id not in valid_unit_ids:
                    return Response(
                        {"units": f"Unit {unit_id} does not belong to this course."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                CourseUnit.objects.filter(pk=unit_id).update(order=unit_index)

                lesson_ids = unit_entry.get("lessons") or []
                for lesson_index, lesson_id in enumerate(lesson_ids):
                    lesson_id = str(lesson_id)
                    if lesson_id not in valid_lesson_ids:
                        return Response(
                            {"lessons": f"Lesson {lesson_id} does not belong to this course."},
                            status=status.HTTP_400_BAD_REQUEST,
                        )
                    Lessons.objects.filter(pk=lesson_id).update(
                        course_unit_id=unit_id, order=lesson_index
                    )

        return Response(CourseDetailSerializer(self.get_object()).data, status=status.HTTP_200_OK)
