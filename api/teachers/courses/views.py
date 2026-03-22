import traceback

from rest_framework import viewsets, status
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.course.models.course import Course
from common.permission import IsCourseTeacherOrAdmin
from common.serializers.courses.course import CourseCreateSerializer, CourseUpdateSerializer, CourseDetailSerializer


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