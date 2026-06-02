from rest_framework import viewsets
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from apps.course.models.lessons import Lessons
from common.serializers.courses.lessons import LessonCreateSerializer, LessonUpdateSerializer, LessonsSerializer


class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lessons.objects.all()
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    http_method_names = ["get", "post", "patch", "delete"]

    def get_serializer_class(self):
        if self.action == "create":
            return LessonCreateSerializer

        elif self.action in ["update", "partial_update"]:
            return LessonUpdateSerializer

        return LessonsSerializer
